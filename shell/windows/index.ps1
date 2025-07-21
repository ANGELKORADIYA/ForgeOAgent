# PowerShell Prompt Processing Script
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName PresentationFramework

function Show-MessageBox {
    param(
        [string]$Message,
        [string]$Title = "Prompt Processor",
        [string]$Type = "Information"
    )
    
    $IconType = switch ($Type) {
        "Error" { [System.Windows.Forms.MessageBoxIcon]::Error }
        "Warning" { [System.Windows.Forms.MessageBoxIcon]::Warning }
        "Information" { [System.Windows.Forms.MessageBoxIcon]::Information }
        default { [System.Windows.Forms.MessageBoxIcon]::Information }
    }
    
    [System.Windows.Forms.MessageBox]::Show($Message, $Title, [System.Windows.Forms.MessageBoxButtons]::OK, $IconType)
}

function Show-PromptTypeDialog {
    param([array]$PromptTypes)
    
    # Create the form
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Select Prompt Type"
    $form.Size = New-Object System.Drawing.Size(400, 300)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    
    # Create ListBox for prompt types
    $listBox = New-Object System.Windows.Forms.ListBox
    $listBox.Location = New-Object System.Drawing.Point(10, 10)
    $listBox.Size = New-Object System.Drawing.Size(360, 180)
    $listBox.SelectionMode = "One"
    foreach ($type in $PromptTypes) {
        $listBox.Items.Add($type) | Out-Null
    }
    $form.Controls.Add($listBox)
    
    # Create OK button
    $okButton = New-Object System.Windows.Forms.Button
    $okButton.Location = New-Object System.Drawing.Point(130, 200)
    $okButton.Size = New-Object System.Drawing.Size(75, 25)
    $okButton.Text = "OK"
    $okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $okButton.Add_Click({
        if ($listBox.SelectedItem) {
            $form.Tag = @{
                SelectedType = $listBox.SelectedItem.ToString()
                UseNew = $false
            }
        }
    })
    $form.Controls.Add($okButton)
    
    # Create New button
    $newButton = New-Object System.Windows.Forms.Button
    $newButton.Location = New-Object System.Drawing.Point(50, 200)
    $newButton.Size = New-Object System.Drawing.Size(75, 25)
    $newButton.Text = "New"
    $newButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $newButton.Add_Click({
        if ($listBox.SelectedItem) {
            $form.Tag = @{
                SelectedType = $listBox.SelectedItem.ToString()
                UseNew = $true
            }
        }
    })
    $form.Controls.Add($newButton)
    
    # Create Cancel button
    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Location = New-Object System.Drawing.Point(210, 200)
    $cancelButton.Size = New-Object System.Drawing.Size(75, 25)
    $cancelButton.Text = "Cancel"
    $cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $form.Controls.Add($cancelButton)
    
    # Set default button and cancel button
    $form.AcceptButton = $okButton
    $form.CancelButton = $cancelButton
    
    # Enable double-click to select
    $listBox.Add_DoubleClick({
        if ($listBox.SelectedItem) {
            $form.Tag = @{
                SelectedType = $listBox.SelectedItem.ToString()
                UseNew = $false
            }
            $form.DialogResult = [System.Windows.Forms.DialogResult]::OK
            $form.Close()
        }
    })
    
    # Show the dialog
    $result = $form.ShowDialog()
    
    if ($result -eq [System.Windows.Forms.DialogResult]::OK -and $form.Tag) {
        return $form.Tag
    }
    
    return $null
}

try {
    # Get selected text from clipboard
    $selectedText = Get-Clipboard -Raw
    if (-not $selectedText) {
        Show-MessageBox -Message "Error: No text in clipboard" -Type "Error"
        exit 1
    }

    # Define Python and script paths
    $pythonBin = "..\..\.venv\Scripts\python.exe"
    $scriptPath = "..\..\main.py"

    # Get prompt types
    $promptTypesRaw = & $pythonBin $scriptPath -l 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-MessageBox -Message "Error: Failed to get prompt types`n$promptTypesRaw" -Type "Error"
        exit 1
    }

    # Process prompt types (remove _system_instruction suffix)
    $promptTypes = $promptTypesRaw -split "`n" | Where-Object { $_.Trim() -ne "" } | ForEach-Object { 
        $_.Replace("_system_instruction", "").Trim() 
    }

    if ($promptTypes.Count -eq 0) {
        Show-MessageBox -Message "Error: No prompt types found" -Type "Error"
        exit 1
    }

    # Show custom selection dialog
    $selection = Show-PromptTypeDialog -PromptTypes $promptTypes
    if (-not $selection) {
        Show-MessageBox -Message "Cancelled: No prompt type selected" -Type "Information"
        exit 1
    }

    # Build command arguments
    $args = @("-p", $selection.SelectedType)
    if ($selection.UseNew) {
        $args += "--new"
    }
    $args += $selectedText

    # Process the prompt
    $result = & $pythonBin $scriptPath $args 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-MessageBox -Message "Error: Failed to process prompt`n$result" -Type "Error"
        exit 1
    }

    # Copy result to clipboard
    $result | Set-Clipboard

    # Show success message with indication if --new was used
    $successMessage = if ($selection.UseNew) {
        "Prompt processed with --new flag and copied to clipboard successfully!"
    } else {
        "Prompt processed and copied to clipboard successfully!"
    }
    Show-MessageBox -Message $successMessage -Type "Information"
}
catch {
    Show-MessageBox -Message "Unexpected error: $($_.Exception.Message)" -Type "Error"
    exit 1
}