const navToggle = document.querySelector("[data-nav-toggle]");
const navLinks = document.querySelector("[data-nav-links]");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
}

document.querySelectorAll('input[type="file"]').forEach((input) => {
  input.addEventListener("change", () => {
    const label = input.closest("label");
    const target = label ? label.querySelector("[data-file-name]") : null;
    if (target && input.files.length) {
      target.textContent = input.files[0].name;
    }
  });
});

const startTransferProgress = (form) => {
  const rings = form.querySelectorAll(".loader-ring");
  const labels = form.querySelectorAll(".loader-percent");
  let progress = 0;

  const render = () => {
    rings.forEach((ring) => ring.style.setProperty("--progress", progress));
    labels.forEach((label) => {
      label.textContent = `${Math.round(progress)}%`;
    });
  };

  render();
  window.setInterval(() => {
    if (progress < 92) {
      progress += Math.max(1, (92 - progress) * 0.08);
      render();
    }
  }, 160);
};

document.querySelectorAll(".js-loading-form").forEach((form) => {
  form.addEventListener("submit", () => {
    form.classList.add("is-loading");
    startTransferProgress(form);
    form.querySelectorAll("button[type='submit']").forEach((button) => {
      button.disabled = true;
    });
  });
});

const footballForm = document.querySelector("[data-football-form]");

if (footballForm) {
  const progressBar = footballForm.querySelector("[data-football-progress-bar]");
  const progressTitle = footballForm.querySelector("[data-football-progress-title]");
  const progressMessage = footballForm.querySelector("[data-football-progress-message]");
  const progressPercent = footballForm.querySelector("[data-football-progress-percent]");
  const progressFrames = footballForm.querySelector("[data-football-progress-frames]");
  const progressRemaining = footballForm.querySelector("[data-football-progress-remaining]");

  const setFootballProgress = (data) => {
    const percent = Number(data.percent || 0);
    const total = Number(data.total_frames || 0);
    const processed = Number(data.processed_frames || 0);
    const remaining = data.remaining_frames === null || data.remaining_frames === undefined
      ? Math.max(0, total - processed)
      : Number(data.remaining_frames);

    if (progressBar) progressBar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
    if (progressPercent) progressPercent.textContent = `${percent.toFixed(1)}%`;
    if (progressFrames) progressFrames.textContent = `${processed} / ${total}`;
    if (progressRemaining) progressRemaining.textContent = `${remaining}`;
    if (progressMessage) progressMessage.textContent = data.message || "Processing video...";
    if (progressTitle && data.status === "finalizing") progressTitle.textContent = "Finalizing outputs...";
    if (progressTitle && data.status === "completed") progressTitle.textContent = "Processing complete";
  };

  const pollFootballJob = async (statusUrl) => {
    const response = await fetch(statusUrl, { cache: "no-store" });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "Could not read football processing status.");
    }

    setFootballProgress(data);

    if (data.status === "completed" && data.result_url) {
      window.location.href = data.result_url;
      return;
    }

    if (data.status === "failed") {
      throw new Error(data.error || data.message || "Football analysis failed.");
    }

    window.setTimeout(() => pollFootballJob(statusUrl).catch(showFootballError), 1000);
  };

  const showFootballError = (error) => {
    footballForm.classList.remove("is-loading");
    footballForm.querySelectorAll("button[type='submit']").forEach((button) => {
      button.disabled = false;
    });
    if (progressTitle) progressTitle.textContent = "Processing failed";
    if (progressMessage) progressMessage.textContent = error.message || String(error);
  };

  footballForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    footballForm.classList.add("is-loading");
    footballForm.querySelectorAll("button[type='submit']").forEach((button) => {
      button.disabled = true;
    });
    setFootballProgress({
      percent: 0,
      processed_frames: 0,
      total_frames: 0,
      remaining_frames: 0,
      message: "Uploading video and starting analysis...",
    });

    try {
      const response = await fetch(footballForm.action, {
        method: "POST",
        body: new FormData(footballForm),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Could not start football analysis.");
      }
      await pollFootballJob(data.status_url);
    } catch (error) {
      showFootballError(error);
    }
  });
}

const transferMenu = document.querySelector("[data-transfer-menu]");

if (transferMenu) {
  const cards = document.querySelectorAll("[data-transfer-action]");
  const panels = document.querySelectorAll("[data-transfer-panel]");

  const activateTransferAction = (action) => {
    cards.forEach((card) => {
      card.classList.toggle("active", card.dataset.transferAction === action);
    });
    panels.forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.transferPanel === action);
    });
  };

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      activateTransferAction(card.dataset.transferAction);
    });
  });

  activateTransferAction(transferMenu.dataset.activeAction || "predict");
}
