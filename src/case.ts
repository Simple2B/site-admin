import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const cases = () => {
  const $addUserModalElement: HTMLElement =
    document.querySelector('#addCaseModal');
  const $stackModalElement: HTMLElement = document.querySelector('#stackModal');
  const scrfInput: HTMLInputElement = document.querySelector('#csrf_token');

  const $caseEditModalElement: HTMLElement = document.querySelector(
    '#caseEditModalElement',
  );

  const $confirmCaseModalElement: HTMLElement = document.querySelector(
    '#confirm-modal-element',
  );

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
    modalOptions,
  );

  const editCaseModal: ModalInterface = new Modal(
    $caseEditModalElement,
    modalOptions,
  );

  const confirmCaseModal: ModalInterface = new Modal(
    $confirmCaseModalElement,
    modalOptions,
  );

  // callBack on btn is_active and is_main
  const caseConfirmModalListener = (
    event: MouseEvent,
    btnElement: HTMLInputElement,
  ) => {
    event.preventDefault();
    confirmCaseModal.show();
    const caseId = btnElement.getAttribute('data-case-id');
    const caseStatusAtr = btnElement.getAttribute('data-case-status');
    const dataFiled = btnElement.getAttribute('data-field');
    const caseConfirmModalText: HTMLElement = document.querySelector(
      '#confirm-modal-text',
    );
    const closeModalBtn = document.querySelector('#close-confirm-modal-btn');

    const isCaseActive = caseStatusAtr === 'True';

    if (caseConfirmModalText) {
      const text = 'Are you sure you want to';
      if (dataFiled === 'is_active') {
        caseConfirmModalText.textContent = isCaseActive
          ? `${text} deactivate case ${caseId}`
          : `${text} activate case ${caseId}`;
      } else if (dataFiled === 'is_main') {
        caseConfirmModalText.textContent = isCaseActive
          ? `${text} deactivate main case ${caseId}`
          : `${text} activate main case ${caseId}`;
      }
    }

    const agreeConfirmModalBtn = document.querySelector(
      '#agree-confirm-modal-btn',
    );

    const disagreeConfirmModalBtn = document.querySelector(
      '#disagree-confirm-modal-btn',
    );

    const confirmCallback = async () => {
      const formData = new FormData();
      formData.append('field', dataFiled);
      formData.append('csrf_token', scrfInput ? scrfInput.value : '');
      const response = await fetch(`/case/update-status/${caseId}`, {
        method: 'PATCH',
        body: formData,
      });
      if (response.status == 200) {
        location.reload();
      }
    };

    const notConfirmCallback = async () => {
      confirmCaseModal.hide();
      agreeConfirmModalBtn.removeEventListener('click', confirmCallback);
    };

    if (agreeConfirmModalBtn && disagreeConfirmModalBtn && closeModalBtn) {
      agreeConfirmModalBtn.addEventListener('click', confirmCallback);

      disagreeConfirmModalBtn.addEventListener('click', notConfirmCallback);
      closeModalBtn.addEventListener('click', notConfirmCallback);
    }
  };

  const activateCaseButton: NodeListOf<HTMLInputElement> =
    document.querySelectorAll('#activate-case-btn');
  activateCaseButton.forEach(btnElement => {
    btnElement.addEventListener('click', e =>
      caseConfirmModalListener(e, btnElement),
    );
  });

  const mainCaseButton: NodeListOf<HTMLInputElement> =
    document.querySelectorAll('#main-case-btn');
  mainCaseButton.forEach(btnElement => {
    btnElement.addEventListener('click', e =>
      caseConfirmModalListener(e, btnElement),
    );
  });

  const stackButton = document.querySelector('#modal-stack-btn');
  if (stackButton) {
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
        confirmCaseModal.show();
        const caseId = e.getAttribute('data-case-id');
        const caseConfirmModalText: HTMLSpanElement = document.querySelector(
          '#confirm-modal-text',
        );
        const agreeConfirmModalBtn = document.querySelector(
          '#agree-confirm-modal-btn',
        );
        const disagreeConfirmModalBtn = document.querySelector(
          '#disagree-confirm-modal-btn',
        );
        const closeModalBtn = document.querySelector(
          '#close-confirm-modal-btn',
        );

        caseConfirmModalText.textContent = `Are you sure you want to delete case ${caseId}?`;

        if (agreeConfirmModalBtn && disagreeConfirmModalBtn && closeModalBtn) {
          const confirmCallback = async () => {
            const response = await fetch(`/case/delete/${caseId}`, {
              method: 'DELETE',
            });
            if (response.status == 200) {
              location.reload();
            }
          };

          const notConfirmCallback = async () => {
            confirmCaseModal.hide();
            agreeConfirmModalBtn.removeEventListener('click', confirmCallback);
          };
          agreeConfirmModalBtn.addEventListener('click', confirmCallback);

          disagreeConfirmModalBtn.addEventListener('click', notConfirmCallback);
          closeModalBtn.addEventListener('click', notConfirmCallback);
        }
      });
    });
  }
  const editCaseButton = document.querySelectorAll('#edit-case-btn');

  editCaseButton.forEach(e => {
    e.addEventListener('click', async () => {
      editCaseModal.show();

      const caseId = e.getAttribute('data-edit-id');

      console.log(caseId);

      const response = await fetch(`/case/${caseId}`, {
        method: 'GET',
      });
      const caseData = await response.json();

      const listOfStacks = caseData.stacks;
      const listOfScreenshots = caseData.screenshots;

      const title: HTMLInputElement =
        document.querySelector('#edit-case-title');
      const subTitle: HTMLInputElement = document.querySelector(
        '#edit-case-sub-title',
      );
      const description: HTMLInputElement = document.querySelector(
        '#edit-case-description',
      );
      const role: HTMLInputElement = document.querySelector('#edit-case-role');
      const isActive: HTMLInputElement = document.querySelector(
        '#edit-case-is-active',
      );
      const isMain: HTMLInputElement =
        document.querySelector('#edit-case-is-main');
      const stacks = document.querySelectorAll(
        '#stacks input[type="checkbox"]',
      );
      const mainImage: HTMLImageElement = document.querySelector(
        '#edit-case-main-image',
      );
      const previewImage: HTMLImageElement = document.querySelector(
        '#edit-case-preview-image',
      );

      const divCaseScreenShoots = document.querySelector(
        '#edit-case-screenshots',
      );

      listOfScreenshots.forEach((screenshot: string) => {
        const img = document.createElement('img');
        img.src = screenshot;
        if (img) {
          divCaseScreenShoots.appendChild(img);
        }
      });

      const caseIdElement: HTMLInputElement =
        document.querySelector('#caseIdEdit');

      stacks.forEach((checkbox: HTMLInputElement) => {
        const label = checkbox.nextElementSibling.textContent;

        if (listOfStacks.includes(label)) {
          checkbox.checked = true;
        }
      });

      title.value = caseData.title;
      subTitle.value = caseData.sub_title;
      description.value = caseData.description;
      role.value = caseData.role;
      isActive.checked = caseData.is_active;
      isMain.checked = caseData.is_main;
      mainImage.src = caseData.main_image;
      previewImage.src = caseData.preview_image;

      caseIdElement.setAttribute('value', caseId);

      const editModalCloseBtn = document.querySelector('#editCaseModalClose');

      if (editModalCloseBtn) {
        editModalCloseBtn.addEventListener('click', () => {
          editCaseModal.hide();
          while (divCaseScreenShoots.firstChild) {
            divCaseScreenShoots.removeChild(divCaseScreenShoots.firstChild);
          }
        });
      }
    });
  });
};
