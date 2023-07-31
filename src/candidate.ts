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
      console.log('BOOM');
      const url = new URL(window.location.href);
      url.searchParams.set('q', searchInput.value);
      window.location.href = `${url.href}`;
    });
  }
};
