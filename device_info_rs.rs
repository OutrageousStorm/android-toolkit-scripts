// Rust version of device_info
// Compile: rustc device_info_rs.rs -o device_info
// Usage: ./device_info

use std::process::Command;

fn adb(cmd: &str) -> String {
    let output = Command::new("adb")
        .args(&["shell", cmd])
        .output()
        .unwrap_or_default();
    String::from_utf8_lossy(&output.stdout).trim().to_string()
}

fn prop(key: &str) -> String {
    adb(&format!("getprop {}", key))
}

fn main() {
    println!("\n📱 Android Device Info (Rust)\n");

    let data = vec![
        ("Model", prop("ro.product.model")),
        ("Brand", prop("ro.product.brand")),
        ("Android", prop("ro.build.version.release")),
        ("API Level", prop("ro.build.version.sdk")),
        ("CPU Architecture", prop("ro.product.cpu.abi")),
        ("Security Patch", prop("ro.build.version.security_patch")),
        ("Build Type", prop("ro.build.type")),
    ];

    for (key, val) in data {
        println!("  {:<22} {}", key, if val.is_empty() { "—".to_string() } else { val });
    }
    println!();
}
