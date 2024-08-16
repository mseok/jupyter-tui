use std::process::{Command, Output};

pub fn execute_python_code(source: &Vec<String>) -> Output {
    let code = source.join("\n");

    Command::new("python3")
        .arg("-c")
        .arg(code)
        .output()
        .expect("Failed to execute Python code")
}
