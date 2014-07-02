using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;

namespace TestRunner
{
    public partial class TestRunnerForm : Form
    {
        public TestRunnerForm()
        {
            InitializeComponent();
        }

        private void selectSourceButtonClick(object sender, EventArgs e)
        {
            if (selectTestSourceFolder.ShowDialog() == System.Windows.Forms.DialogResult.OK) {
                testSourceDirectory.Text = selectTestSourceFolder.SelectedPath;
                RegistryKey regKey = Registry.CurrentUser;
                regKey = regKey.CreateSubKey("Software\\Saxonica\\Saxon.Net\\TestRunner");
                if (testSuite.Text == "XSLT Test Suite") {
                    regKey.SetValue("XSLTTestDir", selectTestSourceFolder.SelectedPath);
                }
                else if (testSuite.Text == "XQuery Test Suite")
                {
                    regKey.SetValue("XQueryTestDir", selectTestSourceFolder.SelectedPath);
                }
                else if (testSuite.Text == "XML Schema Test Suite")
                {
                    regKey.SetValue("SchemaTestDir", selectTestSourceFolder.SelectedPath);
                }
                else if (testSuite.Text == "FO Test Suite")
                {
                    regKey.SetValue("FOTestDir", selectTestSourceFolder.SelectedPath);
                }
            }
        }

        private void clickRunButton(object sender, EventArgs e)
        {
            FeedbackListener f = new FeedbackListener();
            f.doneLabel = doneLabel;
            f.progressBar = progressBar1;
            f.monitor = monitor;
            doneLabel.Text = "";
            progressBar1.Value = 0;
            runButton.Enabled = false;

            if (testSuite.Text == "XSLT Test Suite") {
                XsltTestSuiteDriver driver = new XsltTestSuiteDriver();
                driver.setFeedbackListener(f);
                driver.go(
                    new String[]{testSourceDirectory.Text, testNamePattern.Text});
            }
            else if (testSuite.Text == "XQuery Test Suite")
            {
                XQueryTestSuiteDriver driver = new XQueryTestSuiteDriver();
                driver.setFeedbackListener(f);
                driver.go(
                    new String[] { testSourceDirectory.Text, resultsDirectory.Text, testNamePattern.Text });
            }
            else if (testSuite.Text == "XML Schema Test Suite")
            {
                SchemaTestSuiteDriver driver = new SchemaTestSuiteDriver();
                driver.setFeedbackListener(f);
                driver.go(
                    new String[] { testSourceDirectory.Text, "-g:" + testNamePattern.Text });
            }
            else if (testSuite.Text == "FO Test Suite")
            {
                RegistryKey regKey = Registry.CurrentUser;
                regKey = regKey.CreateSubKey("Software\\Saxonica\\Saxon.Net\\TestRunner");
                regKey.SetValue("TestCaseName", testNamePattern.Text);
                regKey.SetValue("TestSetName", testSetNamePattern.Text);
                string debugStr = (debugCheckBox.Checked ? "-debug" : "");
                string bytecodeStr = (byteCodeCheckBox.Checked ? "on" : "off");
                bytecodeStr = (byteCodeCheckBox.Checked && debugCheckBox.Checked ? "debug" : bytecodeStr);
                FOTestSuiteDriver driver = new FOTestSuiteDriver();
                driver.setFeedbackListener(f);
                driver.go(
                    new String[] { testSourceDirectory.Text, resultsDirectory.Text, (testNamePattern.TextLength > 0 ? "-t:"+testNamePattern.Text: ""), (testSetNamePattern.TextLength > 0 ? "-s:"+testSetNamePattern.Text : ""), debugStr, "-bytecode:"+bytecodeStr });
            }
            doneLabel.Text = "Done!";
            runButton.Enabled = true;
        }

        private void testSuiteSelected(object sender, EventArgs e)
        {
            RegistryKey regKey = Registry.CurrentUser;
            regKey = regKey.CreateSubKey("Software\\Saxonica\\Saxon.Net\\TestRunner");
            if (testSuite.Text == "XSLT Test Suite")
            {
                testSourceDirectory.Text = (String)regKey.GetValue("XSLTTestDir", "");
                resultsDirectory.Text = (String)regKey.GetValue("XSLTResultsDir", "");
                label6.Visible = false;
                testSetNamePattern.Visible = false;
                debugCheckBox.Visible = false;
                byteCodeCheckBox.Visible = false;
            }
            else if (testSuite.Text == "XQuery Test Suite")
            {
                testSourceDirectory.Text = (String)regKey.GetValue("XQueryTestDir", "");
                resultsDirectory.Text = (String)regKey.GetValue("XQueryResultsDir", "");
                label6.Visible = false;
                testSetNamePattern.Visible = false;
                debugCheckBox.Visible = false;
                byteCodeCheckBox.Visible = false;
            }
            else if (testSuite.Text == "XML Schema Test Suite")
            {
                testSourceDirectory.Text = (String)regKey.GetValue("SchemaTestDir", "");
                resultsDirectory.Text = (String)regKey.GetValue("SchemaResultsDir", "");
                label6.Visible = false;
                testSetNamePattern.Visible = false;
                debugCheckBox.Visible = false;
                byteCodeCheckBox.Visible = false;
            }
            else if (testSuite.Text == "FO Test Suite")
            {
                testSourceDirectory.Text = (String)regKey.GetValue("FOTestDir", "");
                resultsDirectory.Text = (String)regKey.GetValue("FOResultsDir", "");
                label6.Visible = true;
                testSetNamePattern.Visible = true;
                debugCheckBox.Visible = true;
                byteCodeCheckBox.Visible = true;
                testNamePattern.Text = (String)regKey.GetValue("TestCaseName", "");
                testSetNamePattern.Text = (String)regKey.GetValue("TestSetName", "");
            }
        }

        public class FeedbackListener : IFeedbackListener
        {
            public Label doneLabel;
            public ProgressBar progressBar;
            public TextBox monitor;

            public void Feedback(int passed, int failed, int total)
            {
                doneLabel.Text = "Done " + (passed + failed) + " of " + total;
                doneLabel.Refresh();
                progressBar.Minimum = 0;
                progressBar.Maximum = total;
                progressBar.Value = passed + failed;
              //  progressBar.Refresh();
            
            }


            public void Message(String message, bool popup)
            {
                if (monitor.Text.Length > 5000) {
                    monitor.Text = "";
                }
                monitor.Text += message;
                monitor.Select(monitor.Text.Length, 0);
                monitor.ScrollToCaret();
                //monitor.Refresh();
            }
        }

        private void CloseButtonClicked(object sender, EventArgs e)
        {
            Close();
        }

        private void resultsDirectoryButtonClick(object sender, EventArgs e)
        {
            if (selectTestSourceFolder.ShowDialog() == System.Windows.Forms.DialogResult.OK) {
                resultsDirectory.Text = selectTestSourceFolder.SelectedPath;
                RegistryKey regKey = Registry.CurrentUser;
                regKey = regKey.CreateSubKey("Software\\Saxonica\\Saxon.Net\\TestRunner");
                if (testSuite.Text == "XSLT Test Suite") {
                    regKey.SetValue("XSLTResultsDir", selectTestSourceFolder.SelectedPath);
                }
                else if (testSuite.Text == "XQuery Test Suite")
                {
                    regKey.SetValue("XQueryResultsDir", selectTestSourceFolder.SelectedPath);
                }
                else if (testSuite.Text == "FO Test Suite")
                {
                    regKey.SetValue("FOResultsDir", selectTestSourceFolder.SelectedPath);
                }
            }
        }
    }
}
