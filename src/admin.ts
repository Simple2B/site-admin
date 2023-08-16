import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';
import {useConfirmModal} from './utils';

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

  const {openModal} = useConfirmModal();

  const addModal: ModalInterface = new Modal(
    $addAdminModalElement,
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
        const id = button.getAttribute('data-admin-id');
        const modalText = `Are you sure you want to delete admin №${id}?`;

        const confirmCallback = async () => {
          const id = button.getAttribute('data-admin-id');
          const response = await fetch(`/admin/delete/${id}`, {
            method: 'DELETE',
          });
          if (response.status == 200) {
            location.reload();
          }
        };

        openModal(modalText, confirmCallback);
      });
    });
  }
};
