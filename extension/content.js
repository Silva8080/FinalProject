console.log("EasyRead loaded");

// =========================
// テスト用単語エリア
// =========================

const testDiv = document.createElement("div");

testDiv.innerHTML = `
  <span class="easyread-word">apple</span>
  <span class="easyread-word">banana</span>
  <span class="easyread-word">orange</span>
`;

testDiv.style.position = "fixed";
testDiv.style.top = "100px";
testDiv.style.right = "20px";
testDiv.style.backgroundColor = "white";
testDiv.style.color = "black";
testDiv.style.padding = "10px";
testDiv.style.border = "1px solid black";
testDiv.style.borderRadius = "8px";
testDiv.style.zIndex = "99999";

document.body.appendChild(testDiv);

// =========================
// ポップアップ表示
// =========================

function showPopup(data) {
  const oldPopup = document.getElementById("easyread-popup");

  if (oldPopup) {
    oldPopup.remove();
  }

  const popup = document.createElement("div");

  popup.id = "easyread-popup";

  let html = `<h3>${data.word}</h3>`;

  data.senses.forEach((sense) => {
    html += `<p><strong>${sense.type}</strong></p>`;
    html += "<ul>";

    sense.meanings.forEach((meaning) => {
      html += `<li>${meaning}</li>`;
    });

    html += "</ul>";
  });

  if (data.examples.length > 0) {
    html += "<hr>";
    html += "<h4>例文</h4>";

    data.examples.forEach((example) => {
      html += `
        <p>${example.english}</p>
        <p>${example.japanese}</p>
      `;
    });
  }

  popup.innerHTML = html;

  popup.style.position = "fixed";
  popup.style.top = "170px";
  popup.style.right = "20px";
  popup.style.width = "300px";
  popup.style.backgroundColor = "white";
  popup.style.color = "black";
  popup.style.padding = "12px";
  popup.style.border = "1px solid #ccc";
  popup.style.borderRadius = "8px";
  popup.style.boxShadow = "0 2px 10px rgba(0,0,0,0.3)";
  popup.style.zIndex = "99999";

  document.body.appendChild(popup);
}

// =========================
// 字幕監視
// =========================

let lastCaption = "";

setInterval(() => {
  const captions = document.querySelectorAll(".ytp-caption-segment");

  const text = Array.from(captions)
    .map((caption) => caption.textContent)
    .join(" ");

  if (!text || text === lastCaption) {
    return;
  }

  lastCaption = text;

  console.log("字幕:", text);

  const words = text.split(/\s+/);

  console.log("単語一覧:", words);

  const spans = words.map((word) => {
    return `<span class="easyread-word">${word}</span>`;
  });

  console.log(spans.join(" "));
}, 500);

// =========================
// ホバー検知
// =========================

document.addEventListener("mouseover", async (event) => {
  if (!event.target.classList.contains("easyread-word")) {
    return;
  }

  const word = event.target.textContent;

  console.log("ホバー:", word);

  // モックデータ
  const data = {
    word: word,
    senses: [
      {
        type: "noun",
        meanings: ["テスト意味1"]
      },
      {
        type: "noun",
        meanings: ["テスト意味2"]
      }
    ],
    examples: [
      {
        english: `Example sentence with ${word}.`,
        japanese: `${word} を使った例文です。`
      }
    ]
  };

  console.log("辞書データ:", data);

  showPopup(data);
});