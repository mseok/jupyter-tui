use ratatui::style::{Color, Style};
use ratatui::text::{Span, Text};
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::util::ipynb::{Cell, Output};
use crate::util::python::execute_python_code;

pub fn create_paragraph(cell_source: &Vec<String>) -> Paragraph<'_> {
    let text = cell_source.join("");

    Paragraph::new(text).block(Block::default().borders(Borders::ALL).title("Code Cell"))
}

pub fn display_output(cell: &mut Cell) -> Paragraph<'_> {
    let output = execute_python_code(&cell.source);

    let style = if output.status.success() {
        cell.outputs = Some(vec![Output {
            output_type: "execute_result".to_string(),
            text: Some(vec![String::from_utf8_lossy(&output.stdout).to_string()]),
            ename: None,
            evalue: None,
            traceback: None,
        }]);
        Style::default().fg(Color::White)
    } else {
        cell.outputs = Some(vec![Output {
            output_type: "error".to_string(),
            text: Some(vec![String::from_utf8_lossy(&output.stderr).to_string()]),
            ename: Some("Error".to_string()),
            evalue: None,
            traceback: None,
        }]);
        Style::default().fg(Color::Red)
    };

    let content: Vec<String> = match &cell.outputs {
        Some(outputs) => outputs
            .iter()
            .flat_map(|output| {
                output.text.as_ref().map_or(Vec::new(), |text| {
                    text.iter()
                        .map(|line| line.clone())
                        .collect::<Vec<String>>()
                })
            })
            .collect(),
        None => vec![],
    }
    .into();

    let text_content = Text::from(content.join("\n"));

    // for line in &content {
    //     println!("{}", line);
    // }

    // Paragraph::new("hello world!")
    Paragraph::new(text_content)
        .block(Block::default().borders(Borders::ALL).title("Output"))
        .style(style)
}
