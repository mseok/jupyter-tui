use ratatui::style::{Color, Style};
use ratatui::text::{Span, Text};
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::util::ipynb::{Cell, Output};
use crate::util::python::execute_python_code;

// TODO: rename -> create_code_cell
pub fn create_code_cell(cell: &Cell) -> Paragraph<'_> {
    let text = cell.source.join("");
    // println!("{}", text);

    Paragraph::new(text).block(Block::default().borders(Borders::ALL).title("Code Cell"))
}

pub fn get_output_from_code_cell(cell: &Cell) -> Vec<String> {
    let content: Vec<String> = match &cell.output {
        Some(output) => output
            .text
            .as_ref()
            .map_or(Vec::new(), |text| {
                text.iter()
                    .map(|line| line.clone())
                    .collect::<Vec<String>>()
            })
            .into_iter()
            .collect(),
        None => vec![],
    }
    .into();

    content
}

pub fn create_code_output_cell(cell: &Cell) -> Paragraph<'_> {
    let output = get_output_from_code_cell(cell);
    let status: String = match &cell.output {
        Some(output) => output
            .ename
            .as_ref()
            .map_or("Success", |ename| ename.as_str()),
        None => "No Output"
    }
    .into();

    let style = if status == "Success" {
        Style::default().fg(Color::White)
    } else if status == "No Output" {
        Style::default().fg(Color::White)
    } else {
        Style::default().fg(Color::Red)
    };

    let content = output.join("\n");

    Paragraph::new(content)
        .block(Block::default().title("Output"))
        .style(style)
}

pub fn compute_output(cell: &mut Cell) {
    let output = execute_python_code(&cell.source);

    if output.status.success() {
        cell.output = Some(Output {
            output_type: "execute_result".to_string(),
            text: Some(vec![String::from_utf8_lossy(&output.stdout).to_string()]),
            ename: None,
            evalue: None,
            traceback: None,
        });
        Style::default().fg(Color::White)
    } else {
        cell.output = Some(Output {
            output_type: "error".to_string(),
            text: Some(vec![String::from_utf8_lossy(&output.stderr).to_string()]),
            ename: Some("Error".to_string()),
            evalue: None,
            traceback: None,
        });
        Style::default().fg(Color::Red)
    };
}
