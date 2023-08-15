import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

const modalOptions: ModalOptions = {
  backdrop: 'dynamic',
  closable: true,
  onHide: () => {},
  onShow: () => {},
  onToggle: () => {},
};

export const admin = () => {
  const $addAdminModalElement: HTMLElement =
    document.querySelector('#add-admin-modal');

  const $confirmModalElement: HTMLElement = document.querySelector(
    '#confirm-modal-element',
  );

  const addModal: ModalInterface = new Modal(
    $addAdminModalElement,
    modalOptions,
  );

  const confirmModal: ModalInterface = new Modal(
    $confirmModalElement,
    modalOptions,
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
        console.log('delete admin');
        confirmModal.show();
        const confirmModalCloseBtn = document.querySelector(
          '#close-confirm-modal-btn',
        );
        const agreeConfirmModalBtn = document.querySelector(
          '#agree-confirm-modal-btn',
        );
        const disagreeConfirmModalBtn = document.querySelector(
          '#disagree-confirm-modal-btn',
        );

        if (
          confirmModalCloseBtn &&
          agreeConfirmModalBtn &&
          disagreeConfirmModalBtn
        ) {
          const confirmCallback = async () => {
            const id = button.getAttribute('data-admin-id');
            const response = await fetch(`/admin/delete/${id}`, {
              method: 'DELETE',
            });
            if (response.status == 200) {
              location.reload();
            }
          };

          const noTConfirmCallback = () => {
            confirmModal.hide();
            agreeConfirmModalBtn.removeEventListener('click', confirmCallback);
          };
          agreeConfirmModalBtn.addEventListener('click', confirmCallback);

          confirmModalCloseBtn.addEventListener('click', noTConfirmCallback);

          disagreeConfirmModalBtn.addEventListener('click', noTConfirmCallback);
        }
      });
    });
  }
};
