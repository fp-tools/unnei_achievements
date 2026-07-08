#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存のダッシュボードHTML(make_unified_dashboard.py出力)にFirebase Authの
ログインゲートを被せる。Firebase Hosting配信用の別ファイルを生成する
（Cowork内アーティファクト用のdashboard.htmlはそのまま・無認証で使い続ける）。

使い方:
  python add_auth_gate.py 入力HTML 出力HTML

firebase-config.js は同フォルダに別途配置する前提（CI側でfirebase apps:sdkconfigの
出力から生成し、この出力HTMLと同じディレクトリにデプロイする）。
"""
import sys

LOGIN_CSS = """
#authOverlay{position:fixed;inset:0;background:#f4f6f9;z-index:9999;display:flex;
  align-items:center;justify-content:center;font-family:"Segoe UI","Meiryo",sans-serif}
#authBox{background:#fff;border:1px solid #e3e8ee;border-radius:12px;padding:32px 28px;
  width:320px;box-shadow:0 4px 16px rgba(0,0,0,.08)}
#authBox h2{margin:0 0 4px;font-size:18px;color:#1F4E78}
#authBox p{margin:0 0 18px;font-size:12px;color:#67727e}
#authBox input{width:100%;box-sizing:border-box;padding:9px 10px;margin-bottom:10px;
  border:1px solid #d5dce3;border-radius:6px;font-size:14px}
#authBox button{width:100%;padding:10px;background:#1F4E78;color:#fff;border:none;
  border-radius:6px;font-size:14px;cursor:pointer}
#authBox button:hover{background:#173d61}
#authErr{color:#c0392b;font-size:12px;min-height:16px;margin-bottom:6px}
#logoutBar{position:fixed;top:8px;right:12px;z-index:9998;font-size:12px;color:#67727e}
#logoutBar button{margin-left:8px;background:none;border:1px solid #d5dce3;border-radius:6px;
  padding:4px 10px;cursor:pointer;font-size:12px;color:#1F4E78}
"""

LOGIN_HTML = """
<div id="authOverlay">
  <div id="authBox">
    <h2>運営課ダッシュボード</h2>
    <p>社内メールアドレスでログインしてください</p>
    <div id="authErr"></div>
    <input id="authEmail" type="email" placeholder="メールアドレス" autocomplete="username">
    <input id="authPass" type="password" placeholder="パスワード" autocomplete="current-password">
    <button id="authBtn">ログイン</button>
  </div>
</div>
<div id="logoutBar" style="display:none">
  <span id="authUserLabel"></span>
  <button id="logoutBtn">ログアウト</button>
</div>
"""

LOGIN_SCRIPTS = """
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="firebase-config.js"></script>
<script>
(function(){
  firebase.initializeApp(window.FIREBASE_CONFIG);
  var overlay = document.getElementById("authOverlay");
  var appRoot = document.getElementById("appRoot");
  var logoutBar = document.getElementById("logoutBar");
  var errBox = document.getElementById("authErr");

  firebase.auth().onAuthStateChanged(function(user){
    if(user){
      overlay.style.display = "none";
      appRoot.style.display = "block";
      logoutBar.style.display = "block";
      document.getElementById("authUserLabel").textContent = user.email;
    } else {
      overlay.style.display = "flex";
      appRoot.style.display = "none";
      logoutBar.style.display = "none";
    }
  });

  document.getElementById("authBtn").addEventListener("click", function(){
    errBox.textContent = "";
    var email = document.getElementById("authEmail").value.trim();
    var pass = document.getElementById("authPass").value;
    firebase.auth().signInWithEmailAndPassword(email, pass)
      .catch(function(err){ errBox.textContent = "ログインに失敗しました（" + err.code + "）"; });
  });
  document.getElementById("authPass").addEventListener("keydown", function(e){
    if(e.key === "Enter"){ document.getElementById("authBtn").click(); }
  });
  document.getElementById("logoutBtn").addEventListener("click", function(){
    firebase.auth().signOut();
  });
})();
</script>
"""


def wrap(html: str) -> str:
    if "<body" not in html or "</body>" not in html:
        raise ValueError("入力HTMLに<body>が見つかりません")
    head_end = html.index("</head>")
    html = html[:head_end] + f"<style>{LOGIN_CSS}</style>" + html[head_end:]

    body_start = html.index(">", html.index("<body")) + 1
    body_end = html.rindex("</body>")
    body_content = html[body_start:body_end]

    new_body = (
        LOGIN_HTML
        + '<div id="appRoot" style="display:none">'
        + body_content
        + "</div>"
        + LOGIN_SCRIPTS
    )
    return html[:body_start] + new_body + html[body_end:]


def main():
    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path, encoding="utf-8") as f:
        html = f.read()
    out = wrap(html)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK: {out_path} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
