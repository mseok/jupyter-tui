use crossterm::event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode};
use crossterm::terminal::{
    disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen,
};
use ratatui::backend::{Backend, CrosstermBackend};
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::text::Text;
use ratatui::{Frame, Terminal};
use std::error::Error;
use std::io;
use std::time::{Duration, Instant};

mod util {
    pub mod ipynb;
    pub mod python;
}
mod components {
    pub mod cell;
}
mod eventhandler;

use components::cell::{
    compute_output, create_code_cell, create_code_output_cell, get_output_from_code_cell,
};
use eventhandler::handle_key_event;
use util::ipynb::{Cell, Notebook};

fn main() -> Result<(), Box<dyn Error>> {
    // Terminal initialization
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    crossterm::execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Load Notebook
    let mut notebook = Notebook::from_file("/Users/mseok/Desktop/programs/test.ipynb");

    let mut current_cell_idx = 0;

    // Main loop
    loop {
        // Draw UI
        terminal.draw(|f| {
            let size = f.size();

            let constraints = notebook
                .cells
                .iter()
                .flat_map(|cell| {
                    let line_count = cell.source.iter().map(|s| s.lines().count()).sum::<usize>();
                    let outputs = get_output_from_code_cell(cell);
                    let outputs_line_count = outputs.len();
                    let output_additional_line: u16;
                    if outputs_line_count == 0 {
                        output_additional_line = 0;
                    } else {
                        output_additional_line = 2;
                    }
                    vec![
                        Constraint::Length(line_count as u16 + 2),
                        Constraint::Length(outputs_line_count as u16 + output_additional_line),
                    ]
                })
                .collect::<Vec<_>>();

            // 위에서 계산한 constraints를 사용하여 layout을 생성
            let chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints(constraints)
                .split(size);

            if let Some(cell) = notebook.cells.get(current_cell_idx / 2) {
                let paragraph = create_code_cell(cell);
                f.render_widget(paragraph, chunks[current_cell_idx]);

                let output_paragraph = create_code_output_cell(cell);
                f.render_widget(output_paragraph, chunks[current_cell_idx + 1]);

                // let chunk = chunks[current_cell_idx];
                // if chunk.as_size().height == 0 {
                //     // if the cell is not visible, skip rendering
                //     return;
                // }
                // println!("chunk: {:?}", chunk);
                // println!("current_cell_idx: {:?}", current_cell_idx);
            }
        })?;

        // Handle input
        if event::poll(Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Esc => break,
                    KeyCode::Enter => {
                        if let Some(cell) = notebook.cells.get_mut(current_cell_idx) {
                            compute_output(cell);
                        }
                    }
                    KeyCode::Char('w') => {
                        notebook.save_to_file("/Users/mseok/Desktop/programs/new_test.ipynb");
                    }
                    KeyCode::Up => {
                        if current_cell_idx > 0 {
                            // always move by 2 because each cell has 2 components (Code / Output)
                            current_cell_idx -= 2;
                        }
                    }
                    KeyCode::Down => {
                        if current_cell_idx < notebook.cells.len() - 2 {
                            current_cell_idx += 2;
                        }
                    }
                    _ => {}
                }
            }
        }
    }

    // Restore terminal
    disable_raw_mode()?;
    crossterm::execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    Ok(())
}
