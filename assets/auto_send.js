(() => {
  if (window.__autoSendInstalled) return;
  window.__autoSendInstalled = true;

  const SILENCE_MS = 1800;
  const MIN_SPEECH_FRAMES = 3;
  let stream = null;
  let ctx = null;
  let timer = null;
  let active = false;

  const approveButton = () =>
    document.querySelector('[data-testid="stChatInputApproveButton"]');

  function stop() {
    if (timer) clearInterval(timer);
    if (stream) stream.getTracks().forEach((t) => t.stop());
    if (ctx) ctx.close();
    timer = stream = ctx = null;
    active = false;
  }

  async function start() {
    if (active) return;
    active = true;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      active = false;
      return;
    }
    ctx = new AudioContext();
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 1024;
    ctx.createMediaStreamSource(stream).connect(analyser);
    const buf = new Float32Array(analyser.fftSize);
    const startedAt = Date.now();
    let noiseSum = 0;
    let noiseCount = 0;
    let speechFrames = 0;
    let lastVoice = 0;

    timer = setInterval(() => {
      const button = approveButton();
      if (!button) { stop(); return; }
      analyser.getFloatTimeDomainData(buf);
      let sum = 0;
      for (const v of buf) sum += v * v;
      const rms = Math.sqrt(sum / buf.length);
      const now = Date.now();
      if (now - startedAt < 500) { noiseSum += rms; noiseCount++; return; }
      const noise = noiseSum / Math.max(noiseCount, 1);
      const threshold = Math.min(0.06, Math.max(0.02, noise * 2.5));
      if (rms > threshold) { speechFrames++; lastVoice = now; }
      if (speechFrames >= MIN_SPEECH_FRAMES && now - lastVoice > SILENCE_MS) {
        stop();
        button.click();
      }
    }, 100);
  }

  new MutationObserver(() => {
    if (approveButton()) start();
  }).observe(document.body, { childList: true, subtree: true });
})();