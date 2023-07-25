import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const user = () => {
  const $addUserModalElement: HTMLElement =
    document.querySelector('#add-user-modal');

  const addModalOptions: ModalOptions = {
    backdrop: 'static',
    closable: true,
    onHide: () => {
      console.log('modal is hidden');
      const backdrop = document.querySelector('[modal-backdrop]');
      if (backdrop) {
        console.log('here');
        console.log(backdrop);
        backdrop.remove();
      }
      console.log(backdrop);
    },
    onShow: () => {
      console.log('user id: ');
    },
    onToggle: () => {
      console.log('modal has been toggled');
    },
  };

  const addModal: ModalInterface = new Modal(
    $addUserModalElement,
    addModalOptions,
  );

  // opening add user modal
  const addUserButton = document.querySelector('#addUserBtn');
  if (addUserButton) {
    addUserButton.addEventListener('click', () => {
      addModal.show();
    });

    // closing add user modal
    const addModalCloseBtn = document.querySelector('#modalAddCloseButton');
    if (addModalCloseBtn) {
      addModalCloseBtn.addEventListener('click', () => {
        console.log('close');
        addModal.hide();
      });
    }

    // search flow
    const searchInput: HTMLInputElement = document.querySelector(
      '#table-search-users',
    );
    const searchInputButton = document.querySelector(
      '#table-search-user-button',
    );
    if (searchInputButton && searchInput) {
      searchInputButton.addEventListener('click', () => {
        const url = new URL(window.location.href);
        url.searchParams.set('q', searchInput.value);
        window.location.href = `${url.href}`;
      });
    }
    const deleteButtons = document.querySelectorAll('.delete-user-btn');

    deleteButtons.forEach(e => {
      e.addEventListener('click', async () => {
        if (confirm('Are sure?')) {
          let id = e.getAttribute('data-user-id');
          const response = await fetch(`/user/delete/${id}`, {
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
