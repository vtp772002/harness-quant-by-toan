use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode};

const VERSION: &str = env!("CARGO_PKG_VERSION");

fn json_escape(value: &str) -> String {
    value.replace('\\', "\\\\").replace('"', "\\\"")
}

fn git_sha(root: &Path) -> String {
    Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(root)
        .output()
        .ok()
        .filter(|out| out.status.success())
        .map(|out| String::from_utf8_lossy(&out.stdout).trim().to_string())
        .filter(|sha| !sha.is_empty())
        .unwrap_or_else(|| "unknown".to_string())
}

fn discover_root() -> Result<PathBuf, String> {
    let start = env::var_os("QUANT_REPO_ROOT")
        .map(PathBuf::from)
        .unwrap_or(env::current_dir().map_err(|e| format!("current dir: {e}"))?);
    let mut candidate = start.as_path();
    loop {
        if candidate.join("AGENTS.md").is_file() && candidate.join("docs").is_dir() {
            return Ok(candidate.to_path_buf());
        }
        candidate = candidate
            .parent()
            .ok_or_else(|| "could not find repository root (AGENTS.md + docs/)".to_string())?;
    }
}

fn parse_options(args: &[String]) -> Result<(String, HashMap<String, String>), String> {
    let command = args.first().cloned().unwrap_or_else(|| "help".to_string());
    let mut options = HashMap::new();
    let mut i = 1;
    while i < args.len() {
        let item = &args[i];
        if !item.starts_with("--") {
            return Err(format!("unexpected argument: {item}"));
        }
        let raw = &item[2..];
        if let Some((key, value)) = raw.split_once('=') {
            options.insert(key.to_string(), value.to_string());
            i += 1;
            continue;
        }
        if i + 1 >= args.len() || args[i + 1].starts_with("--") {
            return Err(format!("missing value for --{raw}"));
        }
        options.insert(raw.to_string(), args[i + 1].clone());
        i += 2;
    }
    Ok((command, options))
}

fn required_paths() -> Vec<&'static str> {
    vec![
        "AGENTS.md",
        "ARCHITECTURE.md",
        "docs/design-docs/index.md",
        "docs/product-specs/index.md",
        "docs/decisions/README.md",
        "docs/exec-plans/tech-debt-tracker.md",
        "scripts/run-eval.py",
        "scripts/evaluate-quant-harness.py",
        "linters/run_all.py",
        "crates/harness-cli/Cargo.toml",
    ]
}

fn doctor(root: &Path) -> bool {
    let missing: Vec<_> = required_paths()
        .into_iter()
        .filter(|path| !root.join(path).is_file())
        .collect();
    let status = if missing.is_empty() {
        "passed"
    } else {
        "failed"
    };
    println!(
        "{{\"command\":\"doctor\",\"status\":\"{status}\",\"root\":\"{}\",\"missing\":[{}]}}",
        json_escape(&root.display().to_string()),
        missing
            .iter()
            .map(|path| format!("\"{}\"", json_escape(path)))
            .collect::<Vec<_>>()
            .join(",")
    );
    missing.is_empty()
}

fn write_manifest(root: &Path, options: &HashMap<String, String>) -> Result<(), String> {
    let run_id = options
        .get("run-id")
        .cloned()
        .or_else(|| env::var("QUANT_RUN_ID").ok())
        .unwrap_or_else(|| "local".to_string());
    let seed = options
        .get("seed")
        .cloned()
        .or_else(|| env::var("QUANT_SEED").ok())
        .unwrap_or_else(|| "42".to_string());
    if run_id.is_empty() || run_id.contains('/') || run_id.contains('\\') || run_id.contains("..") {
        return Err("run-id must be a non-empty single directory name".to_string());
    }
    seed.parse::<u64>()
        .map_err(|_| "seed must be an unsigned integer".to_string())?;
    let dir = root.join("runs").join(&run_id);
    fs::create_dir_all(&dir).map_err(|e| format!("create {}: {e}", dir.display()))?;
    let manifest = format!(
        "{{\n  \"harness_version\": \"{VERSION}\",\n  \"run_id\": \"{}\",\n  \"seed\": {},\n  \"git_sha\": \"{}\",\n  \"status\": \"created\"\n}}\n",
        json_escape(&run_id), seed, json_escape(&git_sha(root))
    );
    fs::write(dir.join("manifest.json"), manifest).map_err(|e| format!("write manifest: {e}"))?;
    println!(
        "{{\"command\":\"boot\",\"status\":\"passed\",\"run_id\":\"{}\"}}",
        json_escape(&run_id)
    );
    Ok(())
}

fn python_command() -> &'static str {
    for candidate in ["python", "python3"] {
        if Command::new(candidate).arg("--version").output().is_ok() {
            return candidate;
        }
    }
    "python"
}

fn stage(root: &Path, name: &str, program: &str, args: &[&str]) -> bool {
    let status = Command::new(program)
        .args(args)
        .current_dir(root)
        .env("PYTHONPATH", ".")
        .env("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        .status();
    let passed = status.map(|s| s.success()).unwrap_or(false);
    println!(
        "{{\"command\":\"check\",\"stage\":\"{name}\",\"status\":\"{}\"}}",
        if passed { "passed" } else { "failed" }
    );
    passed
}

fn check(root: &Path, options: &HashMap<String, String>) -> bool {
    if !doctor(root) {
        return false;
    }
    let seed = options.get("seed").map(String::as_str).unwrap_or("42");
    if seed.parse::<u64>().is_err() {
        eprintln!("seed must be an unsigned integer");
        return false;
    }
    let python = python_command();
    let stages = [
        ("linters", vec!["linters/run_all.py"]),
        (
            "tests",
            vec![
                "-m",
                "pytest",
                "tests/",
                "evals/",
                "-q",
                "-p",
                "no:cacheprovider",
            ],
        ),
        ("honest-eval", vec!["scripts/run-eval.py", "--seed", seed]),
        (
            "scorecard",
            vec!["scripts/evaluate-quant-harness.py", "--seed", seed],
        ),
    ];
    let core_ok = stage(
        root,
        "rust-core-build",
        "cargo",
        &[
            "build",
            "--release",
            "--manifest-path",
            "crates/quant-core/Cargo.toml",
        ],
    );
    let rust_ok = stage(
        root,
        "rust-tests",
        "cargo",
        &["test", "--manifest-path", "crates/harness-cli/Cargo.toml"],
    );
    core_ok
        && rust_ok
        && stages
            .iter()
            .all(|(name, args)| stage(root, name, python, args))
}

fn usage() {
    println!("quant-harness {VERSION}");
    println!("usage: quant-harness <doctor|boot|check> [--seed N] [--run-id ID] [--root PATH]");
}

fn run() -> Result<bool, String> {
    let raw: Vec<String> = env::args().skip(1).collect();
    let (command, options) = parse_options(&raw)?;
    if command == "help" || command == "--help" {
        usage();
        return Ok(true);
    }
    let root = options
        .get("root")
        .map(PathBuf::from)
        .map(Ok)
        .unwrap_or_else(discover_root)?;
    match command.as_str() {
        "doctor" => Ok(doctor(&root)),
        "boot" | "manifest" => write_manifest(&root, &options).map(|_| true),
        "check" => Ok(check(&root, &options)),
        other => Err(format!("unknown command: {other}")),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => ExitCode::from(1),
        Err(error) => {
            eprintln!("quant-harness: {error}");
            ExitCode::from(2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{parse_options, required_paths};

    #[test]
    fn parses_seed_and_run_id() {
        let args = vec![
            "boot".to_string(),
            "--seed=7".to_string(),
            "--run-id".to_string(),
            "r1".to_string(),
        ];
        let (command, options) = parse_options(&args).expect("valid options");
        assert_eq!(command, "boot");
        assert_eq!(options.get("seed"), Some(&"7".to_string()));
        assert_eq!(options.get("run-id"), Some(&"r1".to_string()));
    }

    #[test]
    fn rejects_missing_option_value() {
        let args = vec!["boot".to_string(), "--seed".to_string()];
        assert!(parse_options(&args).is_err());
    }

    #[test]
    fn required_contract_is_repository_relative() {
        assert!(required_paths().contains(&"AGENTS.md"));
        assert!(required_paths().contains(&"scripts/run-eval.py"));
    }
}
