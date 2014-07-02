using System;
using System.Collections.Generic;
using System.Text;

namespace TestRunner
{
    public interface IFeedbackListener
    {
        void Feedback(int passed, int failed, int total);

        void Message(String message, bool popup);
    }
}
