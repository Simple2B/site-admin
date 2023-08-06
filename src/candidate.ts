export const candidate = () => {
  // // search flow
  const searchInput: HTMLInputElement = document.querySelector(
    '#table-search-candidates',
  );
  const searchInputButton = document.querySelector(
    '#table-search-candidates-button',
  );
  if (searchInputButton && searchInput) {
    searchInputButton.addEventListener('click', () => {
      const url = new URL(window.location.href);
      url.searchParams.set('q', searchInput.value);
      window.location.href = `${url.href}`;
    });
  }
  // delte flow
  const deleteButtons = document.querySelectorAll('#delete-candidate-btn');
  if (deleteButtons) {
    deleteButtons.forEach(button => {
      button.addEventListener('click', async () => {
        if (confirm('Are sure?')) {
          let id = button.getAttribute('data-candidate-id');
          const response = await fetch(`/candidate/delete/${id}`, {
            method: 'DELETE',
          });
          if (response.status == 200) {
            location.reload();
          }
        }
      });
    });
  }
};
