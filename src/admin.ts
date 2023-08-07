import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const admin = () => {
  const $addAdminModalElement: HTMLElement =
    document.querySelector('#add-admin-modal');

  const addModalOptions: ModalOptions = {
    backdrop: 'dynamic',
    closable: true,
    onHide: () => {},
    onShow: () => {},
    onToggle: () => {},
  };

  const addModal: ModalInterface = new Modal(
    $addAdminModalElement,
    addModalOptions,
  );

  // opening add user modal
  const addAdminButton = document.querySelector('#add-admin-btn');
  if (addAdminButton) {
    addAdminButton.addEventListener('click', () => {
      addModal.show();
    });

    // closing add user modal
    const addModalCloseBtn = document.querySelector('#modalAddCloseButton');
    if (addModalCloseBtn) {
      addModalCloseBtn.addEventListener('click', () => {
        addModal.hide();
      });
    }
  }
  // delete admin
  const deleteAdminButtons = document.querySelectorAll('#delete-admin-btn');
  if (deleteAdminButtons) {
    deleteAdminButtons.forEach(button => {
      button.addEventListener('click', async () => {
        if (confirm('Are sure?')) {
          let id = button.getAttribute('data-admin-id');
          const response = await fetch(`/admin/delete/${id}`, {
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
