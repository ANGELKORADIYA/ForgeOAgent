# PowerShell Prompt Processing Script
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName PresentationFramework

function Show-MessageBox {
    param(
        [string]$Message,
        [string]$Title = "AI Prompt Helper",
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

function Get-UserPrompt {
    param(
        [string]$ClipboardText = ""
    )
    
    # Create input dialog
    $inputBox = New-Object System.Windows.Forms.Form
    $inputBox.Text = "AI Prompt Helper"
    $inputBox.Size = New-Object System.Drawing.Size(600, 600)
    $inputBox.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $inputBox.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
    $inputBox.MaximizeBox = $false
    $inputBox.MinimizeBox = $false
    
    # Title label
    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Text = "Enter your prompt:"
    $titleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $titleLabel.Location = New-Object System.Drawing.Point(20, 20)
    $titleLabel.Size = New-Object System.Drawing.Size(400, 25)
    
    # Context section
    $contextSectionLabel = New-Object System.Windows.Forms.Label
    $contextSectionLabel.Text = "Context from clipboard:"
    $contextSectionLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $contextSectionLabel.Location = New-Object System.Drawing.Point(20, 50)
    $contextSectionLabel.Size = New-Object System.Drawing.Size(200, 20)
    
    # Clipboard content display
    $clipboardBox = New-Object System.Windows.Forms.TextBox
    $clipboardBox.Location = New-Object System.Drawing.Point(20, 75)
    $clipboardBox.Size = New-Object System.Drawing.Size(540, 120)
    $clipboardBox.Multiline = $true
    $clipboardBox.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
    $clipboardBox.ReadOnly = $true
    $clipboardBox.BackColor = [System.Drawing.Color]::LightGray
    $clipboardBox.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    if ($ClipboardText.Trim() -ne "") {
        $clipboardBox.Text = $ClipboardText
    } else {
        $clipboardBox.Text = "(No clipboard content)"
    }
    
    # Prompt section label
    $promptSectionLabel = New-Object System.Windows.Forms.Label
    $promptSectionLabel.Text = "Your prompt:"
    $promptSectionLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $promptSectionLabel.Location = New-Object System.Drawing.Point(20, 210)
    $promptSectionLabel.Size = New-Object System.Drawing.Size(200, 20)
    
    # Text input for prompt
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(20, 235)
    $textBox.Size = New-Object System.Drawing.Size(540, 200)
    $textBox.Multiline = $true
    $textBox.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
    $textBox.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    
    # Status label
    $statusLabel = New-Object System.Windows.Forms.Label
    if ($ClipboardText.Trim() -ne "") {
        $statusLabel.Text = "Context will be included automatically with your prompt"
        $statusLabel.ForeColor = [System.Drawing.Color]::Green
    } else {
        $statusLabel.Text = "No context available - only your prompt will be processed"
        $statusLabel.ForeColor = [System.Drawing.Color]::Orange
    }
    $statusLabel.Location = New-Object System.Drawing.Point(20, 450)
    $statusLabel.Size = New-Object System.Drawing.Size(500, 20)
    $statusLabel.Font = New-Object System.Drawing.Font("Segoe UI", 8)
    
    # Buttons
    $okButton = New-Object System.Windows.Forms.Button
    $okButton.Text = "Process"
    $okButton.Location = New-Object System.Drawing.Point(400, 490)
    $okButton.Size = New-Object System.Drawing.Size(75, 30)
    $okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
    
    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Text = "Cancel"
    $cancelButton.Location = New-Object System.Drawing.Point(485, 490)
    $cancelButton.Size = New-Object System.Drawing.Size(75, 30)
    $cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    
    # Add controls
    $inputBox.Controls.AddRange(@($titleLabel, $contextSectionLabel, $clipboardBox, $promptSectionLabel, $textBox, $statusLabel, $okButton, $cancelButton))
    $inputBox.AcceptButton = $okButton
    $inputBox.CancelButton = $cancelButton
    
    # Focus on text box
    $textBox.Focus()
    
    # Show dialog
    $result = $inputBox.ShowDialog()
    
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
        return $textBox.Text.Trim()
    }
    
    return $null
}

function Get-PromptType {
    param(
        [string]$pythonBin,
        [string]$scriptPath
    )
    # Get available prompt types
    try {
        $promptTypesRaw = & $pythonBin $scriptPath "-l" "--main"
        if (-not $promptTypesRaw) {
            Show-MessageBox -Message "No prompt types retrieved from script." -Type "Error"
            exit 1
        }
        $promptTypes = $promptTypesRaw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
    }
    catch {
        Show-MessageBox -Message "Failed to fetch prompt types: $($_.Exception.Message)" -Type "Error"
        exit 1
    }

    # Prompt user to select a prompt type
    $selectDialog = New-Object System.Windows.Forms.Form
    $selectDialog.Text = "Select Prompt Type"
    $selectDialog.Size = New-Object System.Drawing.Size(400, 400)
    $selectDialog.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen

    $listBox = New-Object System.Windows.Forms.ListBox
    $listBox.Location = New-Object System.Drawing.Point(20, 20)
    $listBox.Size = New-Object System.Drawing.Size(340, 280)
    $listBox.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $listBox.SelectionMode = "One"
    $listBox.Items.AddRange($promptTypes)

    $okBtn = New-Object System.Windows.Forms.Button
    $okBtn.Text = "OK"
    $okBtn.Location = New-Object System.Drawing.Point(190, 320)
    $okBtn.Size = New-Object System.Drawing.Size(75, 30)
    $okBtn.DialogResult = [System.Windows.Forms.DialogResult]::OK

    $cancelBtn = New-Object System.Windows.Forms.Button
    $cancelBtn.Text = "Cancel"
    $cancelBtn.Location = New-Object System.Drawing.Point(285, 320)
    $cancelBtn.Size = New-Object System.Drawing.Size(75, 30)
    $cancelBtn.DialogResult = [System.Windows.Forms.DialogResult]::Cancel

    $selectDialog.Controls.AddRange(@($listBox, $okBtn, $cancelBtn))
    $selectDialog.AcceptButton = $okBtn
    $selectDialog.CancelButton = $cancelBtn

    $resultDialog = $selectDialog.ShowDialog()# This line was missing in the original file, causing the "not working" issue.

    if ($resultDialog -ne [System.Windows.Forms.DialogResult]::OK -or !$listBox.SelectedItem) {
        Show-MessageBox -Message "No prompt type selected. Operation cancelled." -Type "Information"
        exit 1
    }

    return $listBox.SelectedItem
}

try {
    # Get clipboard content
    $clipboardText = ""
    try {
        $clipboardText = Get-Clipboard -Raw -ErrorAction SilentlyContinue
        if (-not $clipboardText) { $clipboardText = "" }
    }
    catch {
        $clipboardText = ""
    }
    # Define Python and script paths
    $pythonBin = "..\..\.venv\Scripts\python.exe"
    $scriptPath = "..\..\main.py"
    $selectedType = Get-PromptType -pythonBin $pythonBin -scriptPath $scriptPath
    if (-not $selectedType) {
        Show-MessageBox -Message "No prompt type selected. Operation cancelled." -Type "Information"
        exit 0
    }
    
    # Get user prompt
    $userPrompt = Get-UserPrompt -ClipboardText $clipboardText # This line was missing in the original file, causing the "not working" issue.
    if (-not $userPrompt -or "$userPrompt".Trim() -eq "false") {
        Show-MessageBox -Message "Operation cancelled" -Type "Information"
        exit 0
    }
    
    # Create final text with context if available
    $finalText = if ($clipboardText.Trim() -ne "") {
        "$userPrompt`n<context>$clipboardText</context>"
    } else {
        $userPrompt
    }
    
    # Show processing message
    Write-Host "Processing prompt... $finalText" -ForegroundColor Green
    
    # Process the prompt using the main functionality
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $pythonBin
        $psi.Arguments = "`"$scriptPath`" `"$finalText`" -p `"$selectedType`" --main"
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        
        $process = [System.Diagnostics.Process]::Start($psi)
        $result = $process.StandardOutput.ReadToEnd()
        $errorResult = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        
        if ($process.ExitCode -eq 0) {
            # Copy result to clipboard
            $result | Set-Clipboard
            
            # Show result in a dialog
            $resultDialog = New-Object System.Windows.Forms.Form
            $resultDialog.Text = "Processing Result"
            $resultDialog.Size = New-Object System.Drawing.Size(700, 500)
            $resultDialog.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
            
            $resultBox = New-Object System.Windows.Forms.TextBox
            $resultBox.Location = New-Object System.Drawing.Point(20, 20)
            $resultBox.Size = New-Object System.Drawing.Size(640, 380)
            $resultBox.Multiline = $true
            $resultBox.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
            $resultBox.ReadOnly = $true
            $resultBox.Text = $result
            $resultBox.Font = New-Object System.Drawing.Font("Segoe UI", 9)
            
            $copyButton = New-Object System.Windows.Forms.Button
            $copyButton.Text = "Copy to Clipboard"
            $copyButton.Location = New-Object System.Drawing.Point(20, 420)
            $copyButton.Size = New-Object System.Drawing.Size(120, 30)
            $copyButton.Add_Click({
                $result | Set-Clipboard
                Show-MessageBox -Message "Result copied to clipboard!" -Type "Information"
            })
            
            $closeButton = New-Object System.Windows.Forms.Button
            $closeButton.Text = "Close"
            $closeButton.Location = New-Object System.Drawing.Point(580, 420)
            $closeButton.Size = New-Object System.Drawing.Size(80, 30)
            $closeButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
            
            $resultDialog.Controls.AddRange(@($resultBox, $copyButton, $closeButton))
            $resultDialog.AcceptButton = $closeButton
            
            $resultDialog.ShowDialog() | Out-Null
            
            Show-MessageBox -Message "Processing completed successfully! Result has been copied to clipboard." -Type "Information"
        } else {
            Show-MessageBox -Message "Error: Processing failed`n$errorResult" -Type "Error"
        }
    }
    catch {
        Show-MessageBox -Message "Error: Failed to execute Python script`n$($_.Exception.Message)" -Type "Error"
    }
}
catch {
    Show-MessageBox -Message "Unexpected error: $($_.Exception.Message)" -Type "Error"
    exit 1
}