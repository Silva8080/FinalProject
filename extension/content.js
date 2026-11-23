console.log("EasyRead V3 loaded");

let currentPopup = null;
let currentSentence = "";

// =====================
// API
// =====================

function lookupWord(word, sentence) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      {
        type: "lookup",
        word,
        sentence
      },
      resolve
    );
  });
}

function saveToAnki(data) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      {
        type: "anki",

        data: {
          word: data.word,

          meaning:
            data.senses?.[0]?.meanings?.[0] || "",

          sentence:
            currentSentence || ""
        }
      },

      resolve
    );
  });
}

// =====================
// History
// =====================

async function saveHistory(word) {
  const result =
    await chrome.storage.local.get(
      "history"
    );

  const history =
    result.history || [];

  history.unshift(word);

  const unique =
    [...new Set(history)]
      .slice(0, 30);

  await chrome.storage.local.set({
    history: unique
  });
}

async function getHistory() {
  const result =
    await chrome.storage.local.get(
      "history"
    );

  return result.history || [];
}

// =====================
// Speech
// =====================

function speak(word) {
  speechSynthesis.cancel();

  const utterance =
    new SpeechSynthesisUtterance(
      word
    );

  utterance.lang = "en-US";
  utterance.rate = 1;

  speechSynthesis.speak(
    utterance
  );
}

// =====================
// Popup
// =====================

function removePopup() {
  const popup =
    document.getElementById(
      "easyread-popup"
    );

  if (popup) {
    popup.remove();
  }

  currentPopup = null;
}

async function showPopup(
  data,
  x,
  y
) {
  removePopup();

  const history =
    await getHistory();

  const popup =
    document.createElement("div");

  popup.id =
    "easyread-popup";

  let html = `
    <div
      style="
        display:flex;
        justify-content:
        space-between;
        align-items:center;
      "
    >
      <div
        style="
          font-size:22px;
          font-weight:bold;
        "
      >
        ${data.word}
      </div>

      <button
        id="easyread-speak-btn"
      >
        🔊
      </button>

    </div>

    <hr>
  `;

  data.senses.forEach(
    (sense) => {
      html += `
        <div
          style="
            margin-bottom:12px;
          "
        >
          <div
            style="
              font-weight:bold;
              color:#444;
              margin-bottom:4px;
            "
          >
            ${sense.type}
            ${
                sense.type_ja
                ? ` / ${sense.type_ja}`
                : ""
            }
          </div>

          <ul>
      `;

      sense.meanings.forEach(
        (meaning) => {
          html += `
            <li>
              ${meaning}
            </li>
          `;
        }
      );

      html += `
          </ul>
        </div>
      `;
    }
  );

  if (
    data.examples &&
    data.examples.length > 0
  ) {
    html += `
      <hr>

      <div
        style="
          font-weight:bold;
          margin-bottom:8px;
        "
      >
        例文
      </div>
    `;

    data.examples.forEach(
      (example) => {
        html += `
          <div
            style="
              margin-bottom:12px;
            "
          >
            <div>
              ${example.english}
            </div>

            <div
              style="
                color:#666;
                margin-top:3px;
              "
            >
              ${example.japanese}
            </div>
          </div>
        `;
      }
    );
  }

  html += `
    <button
      id="easyread-anki-btn"
      style="
        width:100%;
        margin-top:8px;
      "
    >
      Ankiに保存
    </button>
  `;

  if (history.length > 0) {

    html += `
      <hr>

      <div
        style="
          font-weight:bold;
          margin-bottom:6px;
        "
      >
        最近調べた単語
      </div>

      <div
        id="easyread-history"
      >
    `;

    history.forEach((word) => {

      html += `
        <div
          class="easyread-history-item"
          data-word="${word}"

          style="
            cursor:pointer;
            margin-bottom:4px;
            color:#0066cc;
          "
        >
          ${word}
        </div>
      `;
    });

    html += `
      </div>
    `;
  }

  popup.innerHTML = html;

  popup.style.position =
    "fixed";

  popup.style.left =
    `${x}px`;

  popup.style.top =
    `${y}px`;

  popup.style.width =
    "380px";

  popup.style.maxHeight =
    "500px";

  popup.style.overflowY =
    "auto";

  popup.style.background =
    "white";

  popup.style.color =
    "black";

  popup.style.padding =
    "15px";

  popup.style.borderRadius =
    "10px";

  popup.style.border =
    "1px solid #ccc";

  popup.style.boxShadow =
    "0 4px 15px rgba(0,0,0,0.25)";

  popup.style.zIndex =
    "999999";

  document.body.appendChild(
  popup
  );

  currentPopup = popup;

  popup.addEventListener(
    "mousedown",
    (event) => {
      event.stopPropagation();
    }
  );

  popup.addEventListener(
    "click",
    (event) => {
      event.stopPropagation();
    }
  );

  // 発音

  document
    .getElementById(
      "easyread-speak-btn"
    )
    .addEventListener(
      "click",
      (event) => {

        event.stopPropagation();

        speak(data.word);
    }
  );


  // Anki保存

  document
    .getElementById(
      "easyread-anki-btn"
    )
    .addEventListener(
      "click",
    async (event) => {

        event.stopPropagation();

        const result =
          await saveToAnki(data);

        if (result) {
          document.getElementById(
            "easyread-anki-btn"
          ).textContent =
            "保存しました";
        }
      }
    );

  // 履歴クリック

  document
    .querySelectorAll(
      ".easyread-history-item"
    )
    .forEach((item) => {

        item.addEventListener(
            "click",
            async (event) => {

                event.stopPropagation();

                const word =
                item.dataset.word;

                const result =
                await lookupWord(
                    word,
                    word
                );

                if (!result) {
                    return;
                }

                showPopup(
                    result,
                    x,
                    y
                );
            }
        );
    });
}

// =====================
// Sentence
// =====================

function getSentence() {

  const selection =
    window.getSelection();

  if (
    !selection ||
    !selection.rangeCount
  ) {
    return "";
  }

  const node =
    selection
      .getRangeAt(0)
      .commonAncestorContainer;

  const element =
    node.nodeType === 1
      ? node
      : node.parentElement;

  return (
    element?.innerText ||
    ""
  );
}

// =====================
// Search
// =====================

async function executeLookup(
  text,
  x,
  y
) {

  if (
    !text ||
    text.length > 100
  ) {
    return;
  }

  const sentence =
    getSentence();

  currentSentence =
    sentence;

  const data =
    await lookupWord(
      text,
      sentence
    );

  if (!data) {
    return;
  }

  await saveHistory(
    data.word
  );

  showPopup(
    data,
    x,
    y
  );
}

// =====================
// Selection Search
// =====================

document.addEventListener(
  "mouseup",
  async (event) => {

    const text =
      window
        .getSelection()
        .toString()
        .trim();

    if (!text) {
      return;
    }

    executeLookup(
      text,
      event.clientX + 10,
      event.clientY + 10
    );
  }
);

// =====================
// Double Click Search
// =====================

document.addEventListener(
  "dblclick",
  async (event) => {

    const text =
      window
        .getSelection()
        .toString()
        .trim();

    if (!text) {
      return;
    }

    executeLookup(
      text,
      event.clientX + 10,
      event.clientY + 10
    );
  }
);

// =====================
// ESC
// =====================

document.addEventListener(
  "keydown",
  (event) => {

    if (
      event.key === "Escape"
    ) {
      removePopup();
    }
  }
);

// =====================
// Outside Click
// =====================

document.addEventListener(
  "click",
  (event) => {

    const popup =
      document.getElementById(
        "easyread-popup"
      );

    if (!popup) {
      return;
    }

    if (
      popup.contains(
        event.target
      )
    ) {
      return;
    }

    removePopup();
  }
);