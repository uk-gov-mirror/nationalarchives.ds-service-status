import { initAll } from "@nationalarchives/frontend/nationalarchives/all.mjs";

initAll();

const rtf1 = new Intl.RelativeTimeFormat("en", {
  localeMatcher: "best fit",
  numeric: "always",
  style: "long",
});

// const updateTimeElements = ($el) => {
//   const date = new Date($el.getAttribute("datetime"));
//   if (date) {
//     const secondsDifference = Math.round(
//       (date.getTime() - new Date().getTime()) / 1000,
//     );
//     let relativeTime = "Just now";

//     if (Math.abs(secondsDifference) >= 604800) {
//       relativeTime = rtf1.format(
//         Math.round(secondsDifference / 604800),
//         "week",
//       );
//     } else if (Math.abs(secondsDifference) >= 86400) {
//       relativeTime = rtf1.format(Math.round(secondsDifference / 86400), "day");
//     } else if (Math.abs(secondsDifference) >= 3600) {
//       relativeTime = rtf1.format(Math.round(secondsDifference / 3600), "hour");
//     } else if (Math.abs(secondsDifference) >= 60) {
//       relativeTime = rtf1.format(Math.round(secondsDifference / 60), "minute");
//     } else if (Math.abs(secondsDifference) > 5) {
//       relativeTime = rtf1.format(secondsDifference, "second");
//     }
//     $el.textContent = relativeTime;
//   }
// };

document.querySelectorAll("time[datetime]").forEach(($el) => {
  $el.setAttribute("title", $el.textContent);
  const date = new Date($el.getAttribute("datetime"));
  if (date) {
    let textContent = `${date.toLocaleDateString("en-GB", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })}`;
    if (date.getHours() || date.getMinutes() || date.getSeconds()) {
      textContent += `, ${date.getHours().toString().padStart(2, "0")}:${date
        .getMinutes()
        .toString()
        .padStart(2, "0")}:${date.getSeconds().toString().padStart(2, "0")}`;
    }
    $el.textContent = textContent;
  }
  // updateTimeElements($el);
  // setInterval(() => {
  //   updateTimeElements($el);
  // }, 1000);
});

const $refreshTimer = document.getElementById("refresh-countdown");
const $refreshTime = document.querySelector(
  "meta[name='tna.page.refresh_time']",
);

/* eslint-disable-next-line max-statements */
const updateRefreshTimer = (refreshTime) => {
  const $ariaLiveEl = document.getElementById("aria-live-refresh");
  const secondsDifference = Math.round(
    (refreshTime.getTime() - new Date().getTime()) / 1000,
  );
  if ($ariaLiveEl) {
    if (secondsDifference === 10) {
      $ariaLiveEl.textContent = `This page will automatically refresh in ${secondsDifference} seconds.`;
    } else if (secondsDifference === 3) {
      $ariaLiveEl.textContent = `Page refreshing in ${secondsDifference} seconds…`;
    }
  }
  if (secondsDifference <= 5) {
    document.querySelectorAll(".tna-refresh-banner__content").forEach(($el) => {
      $el.classList.remove("tna-accent-blue");
      $el.classList.add("tna-accent-yellow");
    });
  }
  if (secondsDifference <= 0) {
    $refreshTimer.textContent = "Refreshing page…";
    window.location.reload();
  } else {
    $refreshTimer.textContent = `Refreshing ${rtf1.format(secondsDifference, "second")}…`;
  }
};

if ($refreshTimer && $refreshTime) {
  const url = new URL(window.location.href);
  if (url.searchParams.has("refresh")) {
    const $generatedTimeEl = document.querySelector(
      "meta[name='tna.response.generated'",
    );
    if ($generatedTimeEl) {
      const generatedTime = new Date($generatedTimeEl.getAttribute("content"));
      if (generatedTime) {
        const refreshTime = new Date(
          generatedTime.getTime() +
            parseInt($refreshTime.getAttribute("content"), 10) * 1000,
        );
        /* eslint-disable-next-line max-depth */
        if (refreshTime) {
          const $ariaLiveEl = document.createElement("p");
          $ariaLiveEl.id = "aria-live-refresh";
          $ariaLiveEl.setAttribute("aria-live", "assertive");
          $ariaLiveEl.setAttribute("role", "status");
          $ariaLiveEl.setAttribute("class", "tna-!--visually-hidden");
          document.body.appendChild($ariaLiveEl);

          updateRefreshTimer(refreshTime);
          setInterval(() => {
            updateRefreshTimer(refreshTime);
          }, 1000);
        }
      }
    }
  }
}
