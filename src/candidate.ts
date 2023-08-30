import {useConfirmModal} from './utils';

export const candidate = () => {
  // search flow
  const searchInput: HTMLInputElement = document.querySelector(
    '#table-search-candidates',
  );
  const searchInputButton = document.querySelector(
    '#table-search-candidates-button',
  );

  const {openModal} = useConfirmModal();

  if (searchInputButton && searchInput) {
    searchInputButton.addEventListener('click', () => {
      const url = new URL(window.location.href);
      url.searchParams.set('q', searchInput.value);
      window.location.href = `${url.href}`;
    });
  }
  // delete candidate
  const deleteButtons = document.querySelectorAll('#delete-candidate-btn');
  deleteButtons.forEach(button => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-candidate-id');

      const textModal = `Are you sure you want to delete candidate ${id}?`;

      const confirmCallback = async () => {
        const response = await fetch(`/candidate/delete/${id}`, {
          method: 'DELETE',
        });
        if (response.status == 200) {
          location.reload();
        }
      };
      openModal(textModal, confirmCallback);
    });
  });
};
