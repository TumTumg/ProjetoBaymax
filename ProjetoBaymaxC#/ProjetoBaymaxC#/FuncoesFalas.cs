using System;
using System.Speech.Synthesis;

public class FuncoesFalas
{
    private SpeechSynthesizer _synthesizer;

    public FuncoesFalas()
    {
        _synthesizer = new SpeechSynthesizer();
        _synthesizer.SetOutputToDefaultAudioDevice();
    }

    public void Falar(string texto)
    {
        _synthesizer.SpeakAsync(texto);
    }
}
