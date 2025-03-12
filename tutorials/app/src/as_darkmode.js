// (function() {
//     function setDarkTheme() {
//         window.addEventListener('load', function () {
//             gradioURL = window.location.href
//             if (!gradioURL.endsWith('?__theme=dark')) {
//                 window.location.replace(gradioURL + '?__theme=dark');
//             }
//         });
//     }

//     // Run the function when the DOM is fully loaded
//     if (document.readyState === "loading") {
//         document.addEventListener("DOMContentLoaded", setDarkTheme);
//     } else {
//         setDarkTheme();
//     }
// })();
window.addEventListener('load', function () {
  gradioURL = window.location.href
  if (!gradioURL.endsWith('?__theme=dark')) {
    window.location.replace(gradioURL + '?__theme=dark');
  }
});