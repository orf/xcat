namespace TestRunner
{
    partial class TestRunnerForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.Windows.Forms.Button showTestFolderDialog;
            System.Windows.Forms.Button resultsDirectoryButton;
            this.label1 = new System.Windows.Forms.Label();
            this.testSuite = new System.Windows.Forms.ListBox();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.selectTestSourceFolder = new System.Windows.Forms.FolderBrowserDialog();
            this.label4 = new System.Windows.Forms.Label();
            this.testNamePattern = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.testSetNamePattern = new System.Windows.Forms.TextBox();
            this.testSourceDirectory = new System.Windows.Forms.TextBox();
            this.runButton = new System.Windows.Forms.Button();
            this.doneLabel = new System.Windows.Forms.Label();
            this.CloseButton = new System.Windows.Forms.Button();
            this.progressBar1 = new System.Windows.Forms.ProgressBar();
            this.resultsDirectory = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.monitor = new System.Windows.Forms.TextBox();
            this.debugCheckBox = new System.Windows.Forms.CheckBox();
            this.byteCodeCheckBox = new System.Windows.Forms.CheckBox();
            showTestFolderDialog = new System.Windows.Forms.Button();
            resultsDirectoryButton = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // showTestFolderDialog
            // 
            showTestFolderDialog.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F);
            showTestFolderDialog.Location = new System.Drawing.Point(466, 138);
            showTestFolderDialog.Name = "showTestFolderDialog";
            showTestFolderDialog.Size = new System.Drawing.Size(36, 29);
            showTestFolderDialog.TabIndex = 7;
            showTestFolderDialog.Text = "...";
            showTestFolderDialog.UseVisualStyleBackColor = true;
            showTestFolderDialog.Click += new System.EventHandler(this.selectSourceButtonClick);
            // 
            // resultsDirectoryButton
            // 
            resultsDirectoryButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F);
            resultsDirectoryButton.Location = new System.Drawing.Point(466, 175);
            resultsDirectoryButton.Name = "resultsDirectoryButton";
            resultsDirectoryButton.Size = new System.Drawing.Size(36, 29);
            resultsDirectoryButton.TabIndex = 14;
            resultsDirectoryButton.Text = "...";
            resultsDirectoryButton.UseVisualStyleBackColor = true;
            resultsDirectoryButton.Click += new System.EventHandler(this.resultsDirectoryButtonClick);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(35, 21);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(207, 20);
            this.label1.TabIndex = 0;
            this.label1.Text = "Saxon .NET Test Runner";
            // 
            // testSuite
            // 
            this.testSuite.FormattingEnabled = true;
            this.testSuite.Items.AddRange(new object[] {
            "XSLT Test Suite",
            "XQuery Test Suite",
            "XML Schema Test Suite",
            "FO Test Suite"});
            this.testSuite.Location = new System.Drawing.Point(269, 94);
            this.testSuite.Name = "testSuite";
            this.testSuite.Size = new System.Drawing.Size(210, 30);
            this.testSuite.TabIndex = 1;
            this.testSuite.SelectedIndexChanged += new System.EventHandler(this.testSuiteSelected);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(142, 94);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(100, 13);
            this.label2.TabIndex = 2;
            this.label2.Text = "Test Suite to be run";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(142, 144);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(73, 13);
            this.label3.TabIndex = 3;
            this.label3.Text = "Test Directory";
            // 
            // selectTestSourceFolder
            // 
            this.selectTestSourceFolder.SelectedPath = "C:\\Users\\ond1\\Desktop";
            this.selectTestSourceFolder.ShowNewFolderButton = false;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(146, 215);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(109, 13);
            this.label4.TabIndex = 4;
            this.label4.Text = "Test Name starts with";
            // 
            // testNamePattern
            // 
            this.testNamePattern.Location = new System.Drawing.Point(268, 216);
            this.testNamePattern.Name = "testNamePattern";
            this.testNamePattern.Size = new System.Drawing.Size(209, 20);
            this.testNamePattern.TabIndex = 5;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(147, 244);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(78, 13);
            this.label6.TabIndex = 6;
            this.label6.Text = "Test Set Name";
            this.label6.Visible = false;
            // 
            // testSetNamePattern
            // 
            this.testSetNamePattern.Location = new System.Drawing.Point(269, 245);
            this.testSetNamePattern.Name = "testSetNamePattern";
            this.testSetNamePattern.Size = new System.Drawing.Size(209, 20);
            this.testSetNamePattern.TabIndex = 7;
            this.testSetNamePattern.Visible = false;
            // 
            // testSourceDirectory
            // 
            this.testSourceDirectory.Location = new System.Drawing.Point(269, 144);
            this.testSourceDirectory.Name = "testSourceDirectory";
            this.testSourceDirectory.Size = new System.Drawing.Size(190, 20);
            this.testSourceDirectory.TabIndex = 8;
            // 
            // runButton
            // 
            this.runButton.Location = new System.Drawing.Point(426, 273);
            this.runButton.Name = "runButton";
            this.runButton.Size = new System.Drawing.Size(76, 34);
            this.runButton.TabIndex = 9;
            this.runButton.Text = "Run";
            this.runButton.UseVisualStyleBackColor = true;
            this.runButton.Click += new System.EventHandler(this.clickRunButton);
            // 
            // doneLabel
            // 
            this.doneLabel.AutoSize = true;
            this.doneLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F);
            this.doneLabel.Location = new System.Drawing.Point(35, 324);
            this.doneLabel.Name = "doneLabel";
            this.doneLabel.Size = new System.Drawing.Size(0, 20);
            this.doneLabel.TabIndex = 10;
            // 
            // CloseButton
            // 
            this.CloseButton.Location = new System.Drawing.Point(508, 273);
            this.CloseButton.Name = "CloseButton";
            this.CloseButton.Size = new System.Drawing.Size(76, 34);
            this.CloseButton.TabIndex = 11;
            this.CloseButton.Text = "Exit";
            this.CloseButton.UseVisualStyleBackColor = true;
            this.CloseButton.Click += new System.EventHandler(this.CloseButtonClicked);
            // 
            // progressBar1
            // 
            this.progressBar1.Location = new System.Drawing.Point(264, 321);
            this.progressBar1.Name = "progressBar1";
            this.progressBar1.Size = new System.Drawing.Size(320, 23);
            this.progressBar1.TabIndex = 12;
            // 
            // resultsDirectory
            // 
            this.resultsDirectory.Location = new System.Drawing.Point(269, 181);
            this.resultsDirectory.Name = "resultsDirectory";
            this.resultsDirectory.Size = new System.Drawing.Size(190, 20);
            this.resultsDirectory.TabIndex = 13;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(142, 181);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(120, 13);
            this.label5.TabIndex = 14;
            this.label5.Text = "Saxon Results Directory";
            // 
            // monitor
            // 
            this.monitor.Location = new System.Drawing.Point(0, 374);
            this.monitor.Multiline = true;
            this.monitor.Name = "monitor";
            this.monitor.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.monitor.Size = new System.Drawing.Size(614, 161);
            this.monitor.TabIndex = 15;
            // 
            // debugCheckBox
            // 
            this.debugCheckBox.AutoSize = true;
            this.debugCheckBox.Location = new System.Drawing.Point(284, 288);
            this.debugCheckBox.Name = "debugCheckBox";
            this.debugCheckBox.Size = new System.Drawing.Size(105, 17);
            this.debugCheckBox.TabIndex = 16;
            this.debugCheckBox.Text = "debugCheckBox";
            this.debugCheckBox.UseVisualStyleBackColor = true;
            this.debugCheckBox.Visible = false;
            // 
            // ByteCodeCheckBox
            // 
            this.byteCodeCheckBox.AutoSize = true;
            this.byteCodeCheckBox.Location = new System.Drawing.Point(182, 288);
            this.byteCodeCheckBox.Name = "byteCodeCheckBox";
            this.byteCodeCheckBox.Size = new System.Drawing.Size(72, 17);
            this.byteCodeCheckBox.TabIndex = 17;
            this.byteCodeCheckBox.Text = "ByteCode";
            this.byteCodeCheckBox.UseVisualStyleBackColor = true;
            this.byteCodeCheckBox.Visible = false;
            // 
            // TestRunnerForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(611, 532);
            this.Controls.Add(this.byteCodeCheckBox);
            this.Controls.Add(this.debugCheckBox);
            this.Controls.Add(this.monitor);
            this.Controls.Add(resultsDirectoryButton);
            this.Controls.Add(this.resultsDirectory);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.progressBar1);
            this.Controls.Add(this.CloseButton);
            this.Controls.Add(this.doneLabel);
            this.Controls.Add(this.runButton);
            this.Controls.Add(showTestFolderDialog);
            this.Controls.Add(this.testSourceDirectory);
            this.Controls.Add(this.testNamePattern);
            this.Controls.Add(this.testSetNamePattern);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.testSuite);
            this.Controls.Add(this.label1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Name = "TestRunnerForm";
            this.Text = "Saxon .NET Test Runner";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ListBox testSuite;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.FolderBrowserDialog selectTestSourceFolder;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox testNamePattern;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox testSetNamePattern;
        private System.Windows.Forms.TextBox testSourceDirectory;
        private System.Windows.Forms.Button runButton;
        private System.Windows.Forms.Label doneLabel;
        private System.Windows.Forms.Button CloseButton;
        private System.Windows.Forms.ProgressBar progressBar1;
        private System.Windows.Forms.TextBox resultsDirectory;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox monitor;
        private System.Windows.Forms.CheckBox debugCheckBox;
        private System.Windows.Forms.CheckBox byteCodeCheckBox;
    }
}

