use crossterm::event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode};
use crossterm::terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen};
use ratatui::backend::{Backend, CrosstermBackend};
use ratatui::Terminal;
use ratatui::{layout::Rect, Frame};
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

use util::ipynb::{Notebook, Cell};
use components::cell::{create_paragraph, display_output};
use eventhandler::handle_key_event;

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

            if let Some(cell) = notebook.cells.get(current_cell_idx) {
                let paragraph = create_paragraph(&cell.source);
                f.render_widget(paragraph, size);

                if let Some(output) = &cell.outputs {
                    let output_paragraph = display_output(&mut notebook.cells[current_cell_idx]);
                    let output_rect = Rect {
                        x: size.x,
                        y: size.y,
                        width: size.width,
                        height: size.height,
                    };
                    f.render_widget(output_paragraph, output_rect);
                }
            }
        })?;

        // Handle input
        if event::poll(Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Esc => break,
                    KeyCode::Enter => {
                        if let Some(cell) = notebook.cells.get_mut(current_cell_idx) {
                            display_output(cell);
                        }
                    }
                    KeyCode::Char('w') => {
                        notebook.save_to_file("/Users/mseok/Desktop/programs/new_test.ipynb");
                    }
                    KeyCode::Up => {
                        if current_cell_idx > 0 {
                            current_cell_idx -= 1;
                        }
                    }
                    KeyCode::Down => {
                        if current_cell_idx < notebook.cells.len() - 1 {
                            current_cell_idx += 1;
                        }
                    }
                    _ => {}
                }
            }
        }
    }

    // Restore terminal
    disable_raw_mode()?;
    crossterm::execute!(terminal.backend_mut(), LeaveAlternateScreen, DisableMouseCapture)?;
    terminal.show_cursor()?;

    Ok(())
}
