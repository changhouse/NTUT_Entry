function processLogin() {
    const bodyText = document.body.innerText || "";
    if (bodyText.includes("登入失敗") || (bodyText.includes("驗證碼") && bodyText.includes("錯誤"))) {
        const links = Array.from(document.querySelectorAll("a, button, input")).filter(el => {
            const text = el.innerText || el.value || "";
            return text.includes("重新登入") || text.includes("重新輸入");
        });
        if (links.length > 0) links[0].click();
        else window.location.href = "https://nportal.ntut.edu.tw/index.do";
        return;
    }

    const muid = document.querySelector('#muid');
    const mpassword = document.querySelector('#mpassword');
    const authcode = document.querySelector('#authcode');
    const btn = document.querySelector('input[type=submit]');
    if (!muid || !mpassword || !authcode || !btn) return;

    const img = Array.from(document.images).find(i => i.src.includes('authImage'));
    if (!img) return;

    let retryCount = 0;
    const maxRetries = 40;
    const originalBtnText = btn.value;

    const doFetch = () => {
        const c = document.createElement('canvas');
        c.width = img.naturalWidth || 140;
        c.height = img.naturalHeight || 40;
        c.getContext('2d').drawImage(img, 0, 0);
        const b64 = c.toDataURL('image/png');

        if (retryCount === 0) btn.value = "連線背景服務中 (首次開機請稍候)...";
        btn.disabled = true;

        fetch("http://127.0.0.1:19222/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: b64 })
        })
        .then(res => res.json())
        .then(data => {
            if (data.username && data.password && data.captcha) {
                muid.value = data.username;
                mpassword.value = data.password;
                authcode.value = data.captcha;

                muid.dispatchEvent(new Event('input', {bubbles: true}));
                mpassword.dispatchEvent(new Event('input', {bubbles: true}));
                authcode.dispatchEvent(new Event('input', {bubbles: true}));

                btn.disabled = false;
                btn.value = originalBtnText;
                btn.click();
            }
        })
        .catch(err => {
            retryCount++;
            if (retryCount < maxRetries) {
                btn.value = `等待系統啟動服務中... (${retryCount}/${maxRetries})`;
                setTimeout(doFetch, 1000);
            } else {
                btn.value = "伺服器無回應，請點擊重試";
                btn.disabled = false;
                btn.onclick = (e) => {
                    e.preventDefault();
                    retryCount = 0;
                    doFetch();
                };
            }
        });
    };

    if (img.complete && img.naturalHeight !== 0) doFetch();
    else img.onload = doFetch;
}
setTimeout(processLogin, 300);