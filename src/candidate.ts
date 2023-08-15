import {Modal} from 'flowbite';
import {ModalOptions} from 'flowbite';

const modalOptions: ModalOptions = {
  backdrop: 'static',
  closable: true,
  onHide: () => {},
  onShow: () => {},
  onToggle: () => {},
};

export const candidate = () => {
  // // search flow
  const searchInput: HTMLInputElement = document.querySelector(
    '#table-search-candidates',
  );
  const searchInputButton = document.querySelector(
    '#table-search-candidates-button',
  );

  const $confirmCaseModalElement: HTMLElement = document.querySelector(
    '#confirm-modal-element',
  );

  const confirmModal = new Modal($confirmCaseModalElement, modalOptions);

  if (searchInputButton && searchInput) {
    searchInputButton.addEventListener('click', () => {
      const url = new URL(window.location.href);
      url.searchParams.set('q', searchInput.value);
      window.location.href = `${url.href}`;
    });
  }
  // delete candidate
  const deleteButtons = document.querySelectorAll('#delete-candidate-btn');
  if (deleteButtons) {
    deleteButtons.forEach(button => {
      button.addEventListener('click', async () => {
        confirmModal.show();
        const id = button.getAttribute('data-candidate-id');
        const caseConfirmModalText: HTMLSpanElement = document.querySelector(
          '#confirm-modal-text',
        );
        const agreeConfirmModalBtn = document.querySelector(
          '#agree-confirm-modal-btn',
        );
        const disagreeConfirmModalBtn = document.querySelector(
          '#disagree-confirm-modal-btn',
        );
        const closeConfirmModalBtn = document.querySelector(
          '#close-confirm-modal-btn',
        );

        caseConfirmModalText.textContent = `Are you sure you want to delete question ${id}?`;

        if (
          agreeConfirmModalBtn &&
          disagreeConfirmModalBtn &&
          closeConfirmModalBtn
        ) {
          const confirmCallback = async () => {
            const response = await fetch(`/candidate/delete/${id}`, {
              method: 'DELETE',
            });
            if (response.status == 200) {
              location.reload();
            }
          };

          const notConfirmCallback = () => {
            confirmModal.hide();
            agreeConfirmModalBtn.removeEventListener('click', confirmCallback);
          };

          agreeConfirmModalBtn.addEventListener('click', confirmCallback);
          disagreeConfirmModalBtn.addEventListener('click', notConfirmCallback);
          closeConfirmModalBtn.addEventListener('click', notConfirmCallback);
        }
      });
    });
  }
};
