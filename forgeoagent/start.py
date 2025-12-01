#!/usr/bin/env python3

import wx
import os
import sys
import threading
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add the parent directories to sys.path to import main.py functions
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    # Import functions from main.py
    from forgeoagent.main import (
        inquirer_using_selected_system_instructions,
        print_available_inquirers,
        print_available_executors,
        auto_import_inquirers,
        GeminiAPIClient,
        AgentManager,
        create_master_executor,
        save_last_executor
    )
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

class PromptProcessorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Prompt Processor")
        self.Maximize(True)
        # Initialize API keys
        self.api_keys = []
        try:
            gemini_keys = os.getenv("GEMINI_API_KEYS")
            if gemini_keys:
                self.api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]
        except Exception as e:
            print(f"Error loading API keys: {e}")
        
        # Auto-import system prompts
        try:
            auto_import_inquirers()
        except Exception as e:
            print(f"Error importing system prompts: {e}")
        
        self.init_ui()
        self.load_prompt_types()
        
        # Center the window
        self.Center()
        
    def init_ui(self):
        # Create main panel
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Mode selection
        mode_box = wx.StaticBox(panel, label="Processing Mode")
        mode_sizer = wx.StaticBoxSizer(mode_box, wx.HORIZONTAL)
        
        self.mode_inquirer = wx.RadioButton(panel, label="Inquirer Mode", style=wx.RB_GROUP)
        self.mode_executor = wx.RadioButton(panel, label="Executor Mode")
        
        mode_sizer.Add(self.mode_inquirer, 0, wx.ALL, 5)
        mode_sizer.Add(self.mode_executor, 0, wx.ALL, 5)
        
        main_sizer.Add(mode_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Prompt type selection
        prompt_box = wx.StaticBox(panel, label="Prompt Type")
        prompt_sizer = wx.StaticBoxSizer(prompt_box, wx.VERTICAL)
        
        self.prompt_choice = wx.Choice(panel)
        self.refresh_btn = wx.Button(panel, label="Refresh Types")
        
        prompt_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        prompt_top_sizer.Add(self.prompt_choice, 1, wx.ALL | wx.EXPAND, 5)
        prompt_top_sizer.Add(self.refresh_btn, 0, wx.ALL, 5)
        
        prompt_sizer.Add(prompt_top_sizer, 0, wx.EXPAND)
        main_sizer.Add(prompt_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Context input section
        context_box = wx.StaticBox(panel, label="Context/Selected Text")
        context_sizer = wx.StaticBoxSizer(context_box, wx.VERTICAL)
        
        context_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.load_file_btn = wx.Button(panel, label="Load File")
        self.get_clipboard_btn = wx.Button(panel, label="Get Clipboard")
        self.clear_context_btn = wx.Button(panel, label="Clear")
        
        context_btn_sizer.Add(self.load_file_btn, 0, wx.ALL, 5)
        context_btn_sizer.Add(self.get_clipboard_btn, 0, wx.ALL, 5)
        context_btn_sizer.Add(self.clear_context_btn, 0, wx.ALL, 5)
        
        context_sizer.Add(context_btn_sizer, 0, wx.EXPAND)
        
        self.context_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 100))
        context_sizer.Add(self.context_text, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(context_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # User input section
        input_box = wx.StaticBox(panel, label="Your Prompt")
        input_sizer = wx.StaticBoxSizer(input_box, wx.VERTICAL)
        
        self.user_input = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 100))
        input_sizer.Add(self.user_input, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(input_sizer, 1, wx.ALL | wx.EXPAND, 5)
        
        # Processing options
        options_box = wx.StaticBox(panel, label="Processing Options")
        options_sizer = wx.StaticBoxSizer(options_box, wx.HORIZONTAL)
        
        self.new_content_cb = wx.CheckBox(panel, label="Process as New Content")
        self.new_content_cb.SetValue(True)
        options_sizer.Add(self.new_content_cb, 0, wx.ALL, 5)
        
        main_sizer.Add(options_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Action buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.process_btn = wx.Button(panel, label="Process")
        self.process_btn.SetDefault()
        
        button_sizer.Add(self.process_btn, 0, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)
        
        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready")
        
        panel.SetSizer(main_sizer)
        
        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_refresh_types, self.refresh_btn)
        self.Bind(wx.EVT_BUTTON, self.on_load_file, self.load_file_btn)
        self.Bind(wx.EVT_BUTTON, self.on_get_clipboard, self.get_clipboard_btn)
        self.Bind(wx.EVT_BUTTON, self.on_clear_context, self.clear_context_btn)
        self.Bind(wx.EVT_BUTTON, self.on_process, self.process_btn)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change, self.mode_inquirer)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change, self.mode_executor)
        
    def capture_print_output(self, func, *args, **kwargs):
        """Capture print output from a function that uses print statements"""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            result = func(*args, **kwargs)
            output = captured_output.getvalue()
            return output, result
        except Exception as e:
            output = captured_output.getvalue()
            raise Exception(f"Function error: {str(e)}\nOutput: {output}")
        finally:
            sys.stdout = old_stdout
        
    def on_mode_change(self, event):
        """Handle mode change and reload prompt types"""
        self.load_prompt_types()
        
    def load_prompt_types(self):
        """Load available prompt types based on selected mode"""
        self.status_bar.SetStatusText("Loading prompt types...")
        
        try:
            if self.mode_executor.GetValue():
                # Executor mode - get agents
                output, _ = self.capture_print_output(print_available_executors)
                lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
                prompt_types = [line for line in lines if line != "No agents found." and line]
            else:
                # Inquirer mode - get system instructions
                output, _ = self.capture_print_output(print_available_inquirers)
                lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
                prompt_types = []
                for line in lines:
                    if "_SYSTEM_INSTRUCTION" in line:
                        # Remove _SYSTEM_INSTRUCTION suffix
                        clean_type = line.replace("_SYSTEM_INSTRUCTION", "")
                        prompt_types.append(clean_type)
            
            # Update the choice control
            self.prompt_choice.Clear()
            for ptype in prompt_types:
                self.prompt_choice.Append(ptype)
                
            if prompt_types:
                self.prompt_choice.SetSelection(0)
                
            self.status_bar.SetStatusText(f"Loaded {len(prompt_types)} prompt types")
            
        except Exception as e:
            wx.MessageBox(f"Failed to load prompt types: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            self.status_bar.SetStatusText("Error loading prompt types")
            
    def on_refresh_types(self, event):
        """Refresh the prompt types list"""
        self.load_prompt_types()
        
    def on_load_file(self, event):
        """Load file content into context"""
        with wx.FileDialog(self, "Choose a file to load",
                          wildcard="All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            
            if dlg.ShowModal() == wx.ID_OK:
                file_path = dlg.GetPath()
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.context_text.SetValue(content)
                    self.status_bar.SetStatusText(f"Loaded file: {file_path}")
                except Exception as e:
                    wx.MessageBox(f"Error reading file: {e}", "Error", wx.OK | wx.ICON_ERROR)
                    
    def on_get_clipboard(self, event):
        """Get text from clipboard"""
        try:
            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                    text_data = wx.TextDataObject()
                    wx.TheClipboard.GetData(text_data)
                    clipboard_text = text_data.GetText()
                    self.context_text.SetValue(clipboard_text)
                    self.status_bar.SetStatusText("Clipboard content loaded")
                else:
                    wx.MessageBox("No text data in clipboard", "Warning", wx.OK | wx.ICON_WARNING)
                wx.TheClipboard.Close()
            else:
                wx.MessageBox("Cannot open clipboard", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Error accessing clipboard: {e}", "Error", wx.OK | wx.ICON_ERROR)
            
    def on_clear_context(self, event):
        """Clear the context text"""
        self.context_text.SetValue("")
        self.status_bar.SetStatusText("Context cleared")
        
    def on_process(self, event):
        """Process the prompt"""
        # Validation
        if self.prompt_choice.GetSelection() == wx.NOT_FOUND:
            wx.MessageBox("Please select a prompt type", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        user_text = self.user_input.GetValue().strip()
        if not user_text:
            wx.MessageBox("Please enter your prompt", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        if not self.api_keys:
            wx.MessageBox("No API keys configured. Please check your .env file.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Prepare the input
        context_text = self.context_text.GetValue().strip()
        selected_type = self.prompt_choice.GetStringSelection()
        
        # Format final text
        if context_text:
            final_text = f"{user_text}\n<context>{context_text}</context>"
        else:
            final_text = user_text
            
        # Disable UI during processing
        self.process_btn.Enable(False)
        self.status_bar.SetStatusText("Processing...")
        
        # Run processing in background thread
        thread = threading.Thread(target=self.process_in_background, 
                                args=(final_text, selected_type))
        thread.daemon = True
        thread.start()
        
    def process_in_background(self, final_text, selected_type):
        """Process the prompt in background thread"""
        try:
            new_content = self.new_content_cb.GetValue()
            result = ""
            
            if self.mode_executor.GetValue():
                # Executor mode - use create_master_executor function
                try:
                    agent_manager = AgentManager()
                    prompt_text_path = None
                    
                    if selected_type and selected_type != "None":
                        try:
                            prompt_text_path = agent_manager.get_agent_path(selected_type)
                        except:
                            prompt_text_path = None
                    
                    # Capture output from create_master_executor
                    output, _ = self.capture_print_output(
                        create_master_executor,
                        self.api_keys,
                        final_text,
                        shell_enabled=True,
                        selected_agent={"agent_name": selected_type} if selected_type != "None" else None,
                        reference_agent_path=prompt_text_path,
                        new_content=new_content
                    )
                    
                    result = output.strip()
                    
                except Exception as e:
                    raise Exception(f"Executor mode processing failed: {str(e)}")
            else:
                # Inquirer mode - use inquirer_using_selected_system_instructions
                try:
                    output, _ = self.capture_print_output(
                        inquirer_using_selected_system_instructions,
                        final_text,
                        self.api_keys,
                        selected_type,
                        new_content
                    )
                    result = output.strip()
                except Exception as e:
                    raise Exception(f"Inquirer mode processing failed: {str(e)}")
            
            # Show result on main thread
            if result:
                wx.CallAfter(self.show_result, result, selected_type)
            else:
                wx.CallAfter(self.show_error, "No output received from processing")
            
        except Exception as e:
            wx.CallAfter(self.show_error, f"Processing failed: {str(e)}")
        finally:
            wx.CallAfter(self.reset_ui)
            
    def reset_ui(self):
        """Reset UI after processing"""
        self.process_btn.Enable(True)
        self.status_bar.SetStatusText("Ready")
        
    def show_error(self, error_msg):
        """Show error message"""
        wx.MessageBox(error_msg, "Error", wx.OK | wx.ICON_ERROR)
        
    def show_result(self, result, selected_type):
        """Show processing result"""
        # Create result dialog
        dlg = ResultDialog(self, result, selected_type,self.mode_executor.GetValue())
        dlg.ShowModal()
        dlg.Destroy()


class ResultDialog(wx.Dialog):
    def __init__(self, parent, result_text, prompt_type, mode_executor):
        super().__init__(parent, title=f"Result - {prompt_type}", 
                        size=(800, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.result_text = result_text
        self.mode_executor = mode_executor
        self.init_ui()
        self.Center()
        
    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Result text
        self.result_ctrl = wx.TextCtrl(panel, value=self.result_text,
                                      style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.result_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.copy_btn = wx.Button(panel, label="Copy to Clipboard")
        if self.mode_executor:
            self.save_btn = wx.Button(panel, label="Save Result")
            button_sizer.Add(self.save_btn, 0, wx.ALL, 5)
        self.close_btn = wx.Button(panel, wx.ID_CLOSE, "Close")
        
        button_sizer.Add(self.copy_btn, 0, wx.ALL, 5)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(self.close_btn, 0, wx.ALL, 5)
        
        sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 10)
        
        panel.SetSizer(sizer)
        
        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_copy, self.copy_btn)
        if self.mode_executor:
            self.Bind(wx.EVT_BUTTON, self.on_save, self.save_btn)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.close_btn)  # Add close logic

    def on_close(self, event):
        """Close the dialog when Close button is pressed"""
        self.EndModal(wx.ID_CLOSE)
        
    def on_copy(self, event):
        """Copy result to clipboard"""
        try:
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(self.result_text))
                wx.TheClipboard.Close()
                wx.MessageBox("Result copied to clipboard", "Success", 
                             wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("Cannot open clipboard", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Error copying to clipboard: {e}", "Error", 
                         wx.OK | wx.ICON_ERROR)
            
    def on_save(self, event):
        """Save the result"""
        dlg = wx.TextEntryDialog(self, "Enter a name for saving this result:", 
                               "Save Result")
        
        if dlg.ShowModal() == wx.ID_OK:
            save_name = dlg.GetValue().strip()
            if save_name:
                try:
                    conversation_id = save_last_executor(save_name)
                    if conversation_id:
                        wx.MessageBox(f"Result saved as: {save_name}", "Success", 
                                     wx.OK | wx.ICON_INFORMATION)
                    else:
                        wx.MessageBox("No conversation to save", "Warning", wx.OK | wx.ICON_WARNING)
                except Exception as e:
                    wx.MessageBox(f"Failed to save result: {e}", "Error", 
                                 wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("Please enter a valid name", "Error", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()


    def OnInit(self):
        frame = PromptProcessorFrame()
        frame.Show()
        return True


def main():
    app = PromptProcessorApp()
    app.MainLoop()


if __name__ == "__main__":
    main()