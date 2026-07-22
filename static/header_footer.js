// Function to fetch and insert header
function insertHeader() {
  fetch('header.html')
    .then(response => response.text())
    .then(html => {
      const headerElement = document.getElementById('header');
      headerElement.innerHTML = html;
    })
    .catch(error => {
      console.error('Error fetching header:', error);
    });
}
<script src="//code.tidio.co/etbzm0gzbovev9bouzbs6pvv0x0qvxnm.js" async></script>
// Function to fetch and insert footer
function insertFooter() {
  fetch('footer.html')
    .then(response => response.text())
    .then(html => {
      const footerElement = document.getElementById('footer');
      footerElement.innerHTML = html;
    })
    .catch(error => {
      console.error('Error fetching footer:', error);
    });
}

// Insert header and footer on page load
window.addEventListener('DOMContentLoaded', () => {
  insertHeader();
  insertFooter();
});
