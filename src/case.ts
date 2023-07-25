import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const cases = () => {
  const $addUserModalElement: HTMLElement =
    document.querySelector('#addCaseModal');
  const $editUserModalElement: HTMLElement =
    document.querySelector('#editCaseModal');

  const modalOptions: ModalOptions = {
    backdrop: 'static',
    closable: true,
    onHide: () => {},
    onShow: () => {},
    onToggle: () => {},
  };

  const addModal: ModalInterface = new Modal(
    $addUserModalElement,
    modalOptions,
  );
  const editModal: ModalInterface = new Modal(
    $editUserModalElement,
    modalOptions,
  );

  // opening add user modal
  const addCaseButton = document.querySelector('#add-case-btn');
  if (addCaseButton) {
    addCaseButton.addEventListener('click', () => {
      addModal.show();
    });

    // closing add user modal
    const addModalCloseBtn = document.querySelector('#modalAddCaseCloseButton');
    if (addModalCloseBtn) {
      addModalCloseBtn.addEventListener('click', () => {
        addModal.hide();
      });
    }

    // // search flow
    // const searchInput: HTMLInputElement = document.querySelector(
    //   '#table-search-users',
    // );
    // const searchInputButton = document.querySelector(
    //   '#table-search-user-button',
    // );
    // if (searchInputButton && searchInput) {
    //   searchInputButton.addEventListener('click', () => {
    //     const url = new URL(window.location.href);
    //     url.searchParams.set('q', searchInput.value);
    //     window.location.href = `${url.href}`;
    //   });
    // }
    // const deleteButtons = document.querySelectorAll('.delete-user-btn');

    // deleteButtons.forEach(e => {
    //   e.addEventListener('click', async () => {
    //     if (confirm('Are sure?')) {
    //       let id = e.getAttribute('data-user-id');
    //       const response = await fetch(`/user/delete/${id}`, {
    //         method: 'DELETE',
    //       });
    //       if (response.status == 200) {
    //         location.reload();
    //       }
    //     }
    //   });
    // });
  }
  const editCaseButton = document.querySelector('#edit-case-btn');
  if (editCaseButton) {
    editCaseButton.addEventListener('click', () => {
      editModal.show();
    });

    // closing add user modal
    const editModalCloseBtn = document.querySelector(
      '#modalEditCaseCloseButton',
    );
    if (editModalCloseBtn) {
      editModalCloseBtn.addEventListener('click', () => {
        editModal.hide();
      });
    }
  }
};
