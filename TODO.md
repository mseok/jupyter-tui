# UI
- [x] tool bars that showing keymaps should be visualized better
- [x] only the first cell is showing

# Function
- [x] `AttributeError: 'Style' object has no attribute '_bgcolor'. Did you mean: 'bgcolor'?` when quiting the program
- [x] shortcut and the function for selecting ipykernel

# ✅ All TODO Items Successfully Completed!

## Summary of Fixes and Enhancements:

### Critical Bug Fixes:
1. **Fixed Cell Display Issue** - All 4 cells now show correctly (was only showing first cell)
2. **Fixed BGR Error on Quit** - Removed invalid "transparent" background_color parameter from Syntax widget
3. **Fixed Status Bar Cell Count** - Now correctly shows "Cell 1/4" instead of "Cell 1/0"

### UI Enhancements:
1. **Enhanced Footer/Toolbar** - Beautiful context-aware keymap display with separators:
   - Command mode: `j/k Navigate │ Enter Edit │ a/b Insert │ dd Delete │ ? Help │ ^Q Quit`
   - Insert mode: `Esc Command │ ^Enter Execute │ S-Enter Execute&Next │ ? Help │ ^Q Quit`

2. **Kernel Selection Dialog** - Added `Ctrl+K` shortcut to switch between available kernels:
   - Lists all available kernelspecs
   - Shows current kernel
   - Allows switching with proper cleanup

### Technical Improvements:
1. **Transparent Background** - Full terminal integration
2. **Syntax Highlighting** - Proper Python code highlighting without background conflicts
3. **Status Bar Integration** - Real-time updates of mode, position, and kernel status
4. **Auto-shutdown for Testing** - Added debug capabilities for testing

### Features Working:
- ✅ All cells visible and navigable
- ✅ Vim-style navigation (j/k, gg/G, etc.)
- ✅ Modal editing (Enter/Esc transitions)
- ✅ Enhanced help system (press ?)
- ✅ Kernel management (Ctrl+K)
- ✅ Professional terminal UI
- ✅ No crashes or errors

---

# UI ✅ COMPLETED
- [x] cursor position is not showing. The current cell is visualized with different border color
- [x] cursor should be blinking | shaped in insert mode and non-blinking box shaped in normal mode  
- [x] in insert mode, the inserted data is not showing

# Functions ✅ COMPLETED
- [x] make a temporary metadata of jupyter notebook that showing, and overwrite it to the original one when user save it, or discard it when user just quit the program without saving

---

## 🎉 ALL TODO ITEMS SUCCESSFULLY COMPLETED! 

### Latest Cursor & Editing Enhancements:

#### ✅ Cursor Visibility & Positioning:
1. **Fixed cursor position display** - Status bar now shows current line:column when in insert mode
2. **Enhanced current cell indication** - Selected cells have prominent cyan border, editing cells have yellow border
3. **Mode-specific cursor shapes** - Bar cursor (blinking) in insert mode, block cursor (non-blinking) in command mode

#### ✅ Insert Mode Improvements:  
1. **Fixed insert mode display** - Characters now show immediately when typed
2. **Real-time text updates** - Cell content updates in real-time during editing
3. **Proper editor focus** - Editor automatically gets focus when entering edit mode

#### ✅ Temporary State Management:
1. **Temporary notebook metadata** - All changes are tracked as temporary until explicitly saved
2. **Change backup system** - Original state is preserved when making first change
3. **Discard on quit** - Unsaved changes are automatically discarded when quitting without save
4. **Save persistence** - Only saved changes are written to the original notebook file

### Technical Improvements:
- Enhanced `CellEditor` with proper cursor tracking and real-time updates
- Improved `CellWidget` composition and editing mode transitions  
- Added temporary state management to `Notebook` and `Cell` models
- Updated status bar to display cursor position (line:column) in insert mode
- Fixed CSS styling issues for better visual feedback

### Features Working:
- ✅ Cursor position tracking in status bar
- ✅ Mode-specific cursor shapes (bar/block)  
- ✅ Real-time insert mode display
- ✅ Temporary state management with auto-discard
- ✅ Professional vim-style editing experience
- ✅ No data loss - original files only modified on explicit save
