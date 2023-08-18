import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const modalOptions: ModalOptions = {
  backdrop: 'static',
  closable: true,
  onHide: () => {},
  onShow: () => {},
  onToggle: () => {},
};

interface IConfirmModal {
  openModal: (textModal: string, confirmCallBack: () => void) => void;
}

const useConfirmModal = (): IConfirmModal => {
  const $confirmCaseModalElement: HTMLElement = document.querySelector(
    '#confirm-modal-element',
  );

  const confirmCaseModal: ModalInterface = new Modal(
    $confirmCaseModalElement,
    modalOptions,
  );

  const openModal = (textModal: string, confirmCallBack: () => void) => {
    confirmCaseModal.show();
    const caseConfirmModalText: HTMLElement = document.querySelector(
      '#confirm-modal-text',
    );
    const closeModalBtn = document.querySelector('#close-confirm-modal-btn');
    const agreeConfirmModalBtn = document.querySelector(
      '#agree-confirm-modal-btn',
    );
    const disagreeConfirmModalBtn = document.querySelector(
      '#disagree-confirm-modal-btn',
    );

    if (
      caseConfirmModalText &&
      agreeConfirmModalBtn &&
      disagreeConfirmModalBtn &&
      closeModalBtn
    ) {
      caseConfirmModalText.innerHTML = textModal;

      const notConfirmCallback = async () => {
        confirmCaseModal.hide();
        agreeConfirmModalBtn.removeEventListener('click', confirmCallBack);
      };

      if (agreeConfirmModalBtn && disagreeConfirmModalBtn && closeModalBtn) {
        agreeConfirmModalBtn.addEventListener('click', confirmCallBack);

        disagreeConfirmModalBtn.addEventListener('click', notConfirmCallback);
        closeModalBtn.addEventListener('click', notConfirmCallback);
      }
    }
  };

  return {openModal};
};

export {useConfirmModal};
