import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const cases = () => {
  const $addUserModalElement: HTMLElement =
    document.querySelector('#addCaseModal');
  const $stackModalElement: HTMLElement =
    document.querySelector('#stackModal');
  const scrfInput: HTMLInputElement =
    document.querySelector('#csrf_token');

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

  const stackModal: ModalInterface = new Modal(
    $stackModalElement,
    modalOptions
  )



  const stackButton = document.querySelector('#modal-stack-btn');
  if ( stackButton ) {
    stackButton.addEventListener('click', () => {
      stackModal.show();
    });

    // closing add stack modal
    const stackModalCloseBtn = document.querySelector('#modalStackCloseButton');
    if (stackModalCloseBtn) {
      stackModalCloseBtn.addEventListener('click', () => {
        stackModal.hide();
      });
    }
  }


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

    // search flow
    const searchInput: HTMLInputElement = document.querySelector(
      '#table-search-cases',
    );
    const searchInputButton = document.querySelector(
      '#table-search-cases-button',
    );
    if (searchInputButton && searchInput) {
      searchInputButton.addEventListener('click', () => {
        const url = new URL(window.location.href);
        url.searchParams.set('q', searchInput.value);
        window.location.href = `${url.href}`;
      });
    }
    const deleteButtons = document.querySelectorAll('#delete-case-btn');

    deleteButtons.forEach(e => {
      e.addEventListener('click', async () => {
        if (confirm('Are sure?')) {
          let id = e.getAttribute('data-case-id');
          const response = await fetch(`/case/delete/${id}`, {
            method: 'DELETE',
          });
          if (response.status == 200) {
            location.reload();
          }
        }
      });
    });
  }
  const editCaseButton = document.querySelectorAll('#edit-active-case-btn');
  editCaseButton.forEach(e => {
    e.addEventListener('change', async () => {
        let id = e.getAttribute('data-case-id');
        const field = e.getAttribute('data-field');
        const formData = new FormData();
        formData.append('field', field);
        formData.append("csrf_token", scrfInput ? scrfInput.value : '',)
        const response = await fetch(`/case/update/${id}`, {
          method: 'PATCH',
          body: formData,
        });
        if (response.status == 200) {
          location.reload();
        }
    });
  });
};
