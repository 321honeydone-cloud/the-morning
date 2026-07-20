#!/usr/bin/env python3
"""Encrypt a morning-brief HTML file behind a PIN gate for static hosting.

Usage: python3 encrypt_brief.py <input.html> <output.html> <PIN>

AES-256-GCM, key derived with PBKDF2-HMAC-SHA256 (600k iterations).
Output is a self-contained index.html: PIN screen + ciphertext + WebCrypto decrypt.
Supports "remember this device" via localStorage (stores the derived key, not the PIN).
"""
import sys, os, json, base64, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITERATIONS = 600_000

# Fixed public salt: constant across daily pushes so "remember this device"
# keeps working (the stored key stays valid). Salt is not a secret; it only
# needs to be unique to this deployment, and the IV is fresh every day.
SALT = hashlib.sha256(b"honeydone-morning-brief-v1").digest()[:16]

def encrypt(html: bytes, pin: str):
    salt = SALT
    key = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, ITERATIONS, dklen=32)
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, html, None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
        "iter": ITERATIONS,
    }

GATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Morning brief</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#F9F9F7;color:#2E2C27;font-family:-apple-system,"Segoe UI",sans-serif;
  min-height:100vh;display:flex;align-items:center;justify-content:center;}
.gate{text-align:center;padding:24px;width:100%;max-width:360px;}
.gate h1{font-family:Georgia,serif;font-weight:600;font-size:26px;margin-bottom:6px;}
.gate p{color:#6B6A63;font-size:14px;margin-bottom:22px;}
.pin{display:flex;gap:10px;justify-content:center;margin-bottom:16px;}
input#pin{font-size:22px;letter-spacing:.45em;text-align:center;width:220px;padding:12px 8px 12px 16px;
  border:1px solid #E1E1DF;border-radius:0;background:#FCFCFB;color:#2E2C27;outline:none;}
input#pin:focus{border-color:#2E2C27;}
button{font-size:15px;padding:12px 26px;border:1px solid #2E2C27;background:#2E2C27;color:#F9F9F7;cursor:pointer;}
button:disabled{opacity:.5;cursor:default;}
label.rem{display:flex;gap:8px;align-items:center;justify-content:center;color:#6B6A63;font-size:13px;margin-top:16px;cursor:pointer;}
.err{color:#C6613F;font-size:13px;min-height:18px;margin-top:12px;}
</style>
</head>
<body>
<div class="gate" id="gate">
  <h1>Morning brief</h1>
  <p>Enter your PIN to unlock today&rsquo;s brief.</p>
  <div class="pin"><input id="pin" type="password" inputmode="numeric" autocomplete="off" autofocus></div>
  <button id="go">Unlock</button>
  <label class="rem"><input type="checkbox" id="rem" checked> Remember this device</label>
  <div class="err" id="err"></div>
</div>
<script>
const DATA = __PAYLOAD__;
const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

async function deriveKey(pin){
  const mat = await crypto.subtle.importKey("raw", new TextEncoder().encode(pin), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    {name:"PBKDF2", salt:b64(DATA.salt), iterations:DATA.iter, hash:"SHA-256"},
    mat, {name:"AES-GCM", length:256}, true, ["decrypt"]);
}
async function tryDecrypt(key){
  const pt = await crypto.subtle.decrypt({name:"AES-GCM", iv:b64(DATA.iv)}, key, b64(DATA.ct));
  const blob = new Blob([pt], {type:"text/html"});
  location.replace(URL.createObjectURL(blob));
}
async function unlock(){
  const pin = document.getElementById("pin").value.trim();
  if(!pin) return;
  const btn = document.getElementById("go");
  btn.disabled = true; document.getElementById("err").textContent = "";
  try{
    const key = await deriveKey(pin);
    if(document.getElementById("rem").checked){
      const raw = await crypto.subtle.exportKey("raw", key);
      try{ localStorage.setItem("mb_k_"+DATA.salt, btoa(String.fromCharCode(...new Uint8Array(raw)))); }catch(e){}
    }
    await tryDecrypt(key);
  }catch(e){
    btn.disabled = false;
    document.getElementById("err").textContent = "That PIN didn't unlock it.";
    document.getElementById("pin").value = ""; document.getElementById("pin").focus();
  }
}
document.getElementById("go").addEventListener("click", unlock);
document.getElementById("pin").addEventListener("keydown", e => { if(e.key === "Enter") unlock(); });
(async () => {   // silent unlock if this device remembered the key for this salt
  try{
    const saved = localStorage.getItem("mb_k_"+DATA.salt);
    if(!saved) return;
    const key = await crypto.subtle.importKey("raw", b64(saved), {name:"AES-GCM"}, true, ["decrypt"]);
    await tryDecrypt(key);
  }catch(e){}
})();
</script>
</body>
</html>
"""

def main():
    src, dst, pin = sys.argv[1], sys.argv[2], sys.argv[3]
    payload = encrypt(open(src, "rb").read(), pin)
    open(dst, "w").write(GATE.replace("__PAYLOAD__", json.dumps(payload)))
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes)")

if __name__ == "__main__":
    main()
