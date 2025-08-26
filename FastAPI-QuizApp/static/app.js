// Add choice field dynamically
function addChoice() {
  const container = document.getElementById("choices");
  const div = document.createElement("div");
  div.classList.add("choice");
  div.innerHTML = `
        <input type="text" class="choice_text" placeholder="Choice text" required>
        <label><input type="checkbox" class="is_correct"> Correct</label>
    `;
  container.appendChild(div);
}

// Submit form
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("questionForm");
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const question_text = document.getElementById("question_text").value;
      const choice_texts = document.querySelectorAll(".choice_text");
      const is_corrects = document.querySelectorAll(".is_correct");

      const choices = [];
      for (let i = 0; i < choice_texts.length; i++) {
        choices.push({
          choice_text: choice_texts[i].value,
          is_correct: is_corrects[i].checked,
        });
      }

      const payload = { question_text, choices };
      const res = await fetch("/questions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      document.getElementById("result").innerText = data.message || "Success!";
      form.reset();
    });
  }
});

// Fetch question and choices
async function fetchQuestion() {
  const id = document.getElementById("question_id").value;
  const questionRes = await fetch(`/questions/${id}`);
  const choicesRes = await fetch(`/choices/${id}`);

  if (!questionRes.ok || !choicesRes.ok) {
    document.getElementById("questionDisplay").innerText =
      "Question not found.";
    return;
  }

  const question = await questionRes.json();
  const choices = await choicesRes.json();

  document.getElementById(
    "questionDisplay"
  ).innerText = `Q: ${question.question_text}`;

  const choicesDiv = document.getElementById("choicesDisplay");
  choicesDiv.innerHTML = "<ul>";
  choices.forEach((choice) => {
    choicesDiv.innerHTML += `<li>${choice.choice_text} ${
      choice.is_correct ? "(Correct)" : ""
    }</li>`;
  });
  choicesDiv.innerHTML += "</ul>";
}
