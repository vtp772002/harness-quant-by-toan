// quant-core: deterministic backtest hot loop, mirror Python evals/gate.py panel_backtest.
// Boundary: CSV in/out (panel.csv, members.csv -> equity.csv + stdout meta). Std only.
// Gia dinh (giong Python): gia > 0, CSV khong chua dau phay trong field, panel sort theo (ts, symbol).
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::env;
use std::fs;
use std::process::ExitCode;

#[derive(Clone)]
struct Bar {
    ts: String,
    close: f64,
    volume: f64,
}

struct Cfg {
    lookback: usize,
    fee_bps: f64,
    spread_bps: f64,
    impact_k: f64,
    stress_m: f64,
    cash: f64,
    min_trade: f64,
    ref_vol: f64,
    base_qty: f64,
    max_pos: f64,
    vol_window: usize,
}

fn arg(args: &HashMap<String, String>, k: &str, d: &str) -> String {
    args.get(k).cloned().unwrap_or_else(|| d.to_string())
}

fn momentum(closes: &[f64], lookback: usize) -> f64 {
    if closes.len() < lookback + 1 {
        return 0.0;
    }
    let past = closes[closes.len() - lookback - 1];
    let last = closes[closes.len() - 1];
    if past == 0.0 {
        return 0.0;
    }
    ((last - past) / past * 10.0).clamp(-1.0, 1.0)
}

fn trailing_vol(c: &[f64], window: usize) -> f64 {
    if c.len() < 6 {
        return 0.01;
    }
    let hist = &c[..c.len() - 1];
    let mut rets: Vec<f64> = hist.windows(2).map(|w| (w[1] - w[0]) / w[0]).collect();
    if rets.len() > window {
        rets.drain(..rets.len() - window);
    }
    if rets.len() <= 1 {
        return 0.01;
    }
    let m = rets.len() as f64;
    let mean = rets.iter().sum::<f64>() / m;
    (rets.iter().map(|x| (x - mean) * (x - mean)).sum::<f64>() / (m - 1.0)).sqrt()
}

fn slip_bps(volume: f64, vol_ratio: f64, qty: f64, cfg: &Cfg) -> (f64, f64) {
    let part = qty.abs() / volume.max(1e-9);
    let vr = vol_ratio.clamp(0.0, 4.0);
    let slip = (cfg.spread_bps * (1.0 + 2.0 * vr) + cfg.impact_k * part.sqrt()) * cfg.stress_m;
    (slip, cfg.fee_bps)
}

fn run() -> Result<(), String> {
    let raw: Vec<String> = env::args().skip(1).collect();
    let mut args = HashMap::new();
    let mut i = 0;
    while i < raw.len() {
        if raw[i].starts_with("--") && i + 1 < raw.len() {
            args.insert(raw[i][2..].to_string(), raw[i + 1].clone());
            i += 2;
        } else {
            i += 1;
        }
    }
    let p = |k: &str, d: &str| arg(&args, k, d);
    let cfg = Cfg {
        lookback: p("lookback", "20")
            .parse()
            .map_err(|e| format!("lookback: {e}"))?,
        fee_bps: p("fee", "2.0").parse().map_err(|e| format!("fee: {e}"))?,
        spread_bps: p("spread", "5.0")
            .parse()
            .map_err(|e| format!("spread: {e}"))?,
        impact_k: p("impact", "50.0")
            .parse()
            .map_err(|e| format!("impact: {e}"))?,
        stress_m: p("stress", "1.0")
            .parse()
            .map_err(|e| format!("stress: {e}"))?,
        cash: p("cash", "1000000")
            .parse()
            .map_err(|e| format!("cash: {e}"))?,
        min_trade: p("min-trade", "25.0")
            .parse()
            .map_err(|e| format!("min-trade: {e}"))?,
        ref_vol: p("ref-vol", "0.01")
            .parse()
            .map_err(|e| format!("ref-vol: {e}"))?,
        base_qty: p("base-qty", "100.0")
            .parse()
            .map_err(|e| format!("base-qty: {e}"))?,
        max_pos: p("max-pos", "1000.0")
            .parse()
            .map_err(|e| format!("max-pos: {e}"))?,
        vol_window: p("vol-window", "20")
            .parse()
            .map_err(|e| format!("vol-window: {e}"))?,
    };
    let panel_path = p("panel", "panel.csv");
    let members_path = p("members", "members.csv");
    let out_path = p("out", "equity.csv");

    let panel_text =
        fs::read_to_string(&panel_path).map_err(|e| format!("read {panel_path}: {e}"))?;
    let mut series: BTreeMap<String, Vec<Bar>> = BTreeMap::new();
    let mut dates_set = BTreeSet::new();
    for (ln, line) in panel_text.lines().enumerate() {
        if ln == 0 || line.trim().is_empty() {
            continue;
        }
        let f: Vec<&str> = line.split(',').collect();
        if f.len() != 4 {
            return Err(format!("panel line {ln}: expect 4 cols"));
        }
        let bar = Bar {
            ts: f[1].to_string(),
            close: f[2].parse().map_err(|e| format!("close line {ln}: {e}"))?,
            volume: f[3].parse().map_err(|e| format!("volume line {ln}: {e}"))?,
        };
        dates_set.insert(bar.ts.clone());
        series.entry(f[0].to_string()).or_default().push(bar);
    }
    let members_text =
        fs::read_to_string(&members_path).map_err(|e| format!("read {members_path}: {e}"))?;
    let mut members: HashMap<String, HashSet<String>> = HashMap::new();
    for (ln, line) in members_text.lines().enumerate() {
        if ln == 0 || line.trim().is_empty() {
            continue;
        }
        let f: Vec<&str> = line.split(',').collect();
        if f.len() != 2 {
            return Err(format!("members line {ln}: expect 2 cols"));
        }
        members
            .entry(f[0].to_string())
            .or_default()
            .insert(f[1].to_string());
    }

    let syms: Vec<String> = series.keys().cloned().collect();
    let mut index: HashMap<String, HashMap<String, usize>> = HashMap::new();
    for s in &syms {
        let mut m = HashMap::new();
        for (k, b) in series[s].iter().enumerate() {
            m.insert(b.ts.clone(), k);
        }
        index.insert(s.clone(), m);
    }
    let dates: Vec<String> = dates_set.into_iter().collect();
    let empty = HashSet::new();
    let mut cash = cfg.cash;
    let mut pos: HashMap<String, f64> = syms.iter().map(|s| (s.clone(), 0.0)).collect();
    let mut fills: u64 = 0;
    let mut turnover = 0.0;
    let mut curve: Vec<(String, f64)> = Vec::with_capacity(dates.len());

    for t in &dates {
        let mem = members.get(t).unwrap_or(&empty);
        let mut px_today: HashMap<&str, f64> = HashMap::new();
        for s in &syms {
            if !mem.contains(s) {
                continue;
            }
            let serie = &series[s];
            let Some(&k) = index[s].get(t) else { continue };
            let closes: Vec<f64> = serie.iter().take(k + 1).map(|b| b.close).collect();
            let target = cfg.base_qty * momentum(&closes, cfg.lookback);
            if target.abs() > cfg.max_pos {
                return Err(format!("RiskBreach: target {target} > max {}", cfg.max_pos));
            }
            if cash <= 0.0 {
                return Err("RiskBreach: cash depleted".to_string());
            }
            let delta = target - pos[s.as_str()];
            let px = serie[k].close;
            if delta.abs() > cfg.min_trade {
                let (slip, fee) = slip_bps(
                    serie[k].volume,
                    trailing_vol(&closes, cfg.vol_window) / cfg.ref_vol,
                    delta,
                    &cfg,
                );
                let adj = if delta > 0.0 {
                    px * (1.0 + (slip + fee) / 1e4)
                } else {
                    px * (1.0 - (slip + fee) / 1e4)
                };
                cash -= delta * adj;
                pos.insert(s.clone(), target);
                fills += 1;
                turnover += delta.abs() * adj;
            }
            px_today.insert(s.as_str(), px);
        }
        let eq = cash
            + syms
                .iter()
                .map(|s| pos[s.as_str()] * px_today.get(s.as_str()).copied().unwrap_or(0.0))
                .sum::<f64>();
        curve.push((t.clone(), eq));
    }

    let mut out = String::from("ts,equity\n");
    for (t, eq) in &curve {
        out.push_str(&format!("{t},{eq}\n"));
    }
    fs::write(&out_path, out).map_err(|e| format!("write {out_path}: {e}"))?;
    println!("fills={fills} turnover={turnover}");
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) if e.starts_with("RiskBreach") => {
            eprintln!("{e}");
            ExitCode::from(2)
        }
        Err(e) => {
            eprintln!("{e}");
            ExitCode::FAILURE
        }
    }
}
