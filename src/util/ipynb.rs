use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fs;

#[derive(Debug, Serialize, Deserialize)]
pub struct Notebook {
    pub cells: Vec<Cell>,
    // 다른 필요한 필드들을 추가할 수 있음
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Cell {
    pub cell_type: String,
    pub source: Vec<String>,
    pub outputs: Option<Vec<Output>>,
    // 필요한 필드 추가
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Output {
    pub output_type: String,
    pub text: Option<Vec<String>>,
    pub ename: Option<String>,
    pub evalue: Option<String>,
    pub traceback: Option<Vec<String>>,
    // 필요한 필드 추가
}

impl Notebook {
    pub fn from_file(path: &str) -> Self {
        let data = fs::read_to_string(path).expect("Unable to read file");
        serde_json::from_str(&data).expect("Unable to parse JSON")
    }

    pub fn save_to_file(&self, path: &str) {
        let data = serde_json::to_string_pretty(self).expect("Unable to serialize to JSON");
        fs::write(path, data).expect("Unable to write file");
    }
}

