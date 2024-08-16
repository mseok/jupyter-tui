use crossterm::event::{KeyCode, KeyEvent};
use crate::util::ipynb::Notebook;

pub fn handle_key_event(key: KeyEvent, notebook: &mut Notebook) {
    match key.code {
        KeyCode::Enter => {
            // 현재 선택된 셀의 코드를 실행하고 결과를 표시
        }
        KeyCode::Char('w') => {
            notebook.save_to_file("output.ipynb");
        }
        _ => {}
    }
}
