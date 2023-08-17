import {Modal} from 'flowbite';
import type {ModalInterface} from 'flowbite';
import {modalOptions, useConfirmModal} from './utils';

interface ICaseScreenshot {
  id: number;
  url: string;
}

interface ICaseOut {
  id: number;
  title: string;
  sub_title: string;
  description: string;
  is_active: boolean;
  is_main: boolean;
  project_link: string;
  role: string;
  stacks_names: string[];
  screenshots: ICaseScreenshot[];
  main_image_url: string;
  preview_image_url: string;
}

const createCaseScreenshot = (screenshot: ICaseScreenshot): HTMLElement => {
  const screenshotDiv = document.createElement('div');
  screenshotDiv.setAttribute('class', 'flex flex-col');
  const img = document.createElement('img');
  const deleteBtn = document.createElement('div');
  deleteBtn.id = 'edit-case-screenshot-delete-icon';
  deleteBtn.setAttribute(
    'class',
    'px-3 py-2 text-xs font-medium text-center text-white bg-red-700 rounded-lg hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800',
  );
  deleteBtn.innerHTML = 'Delete';
  img.src = screenshot.url;
  screenshotDiv.appendChild(img);
  screenshotDiv.appendChild(deleteBtn);

  deleteBtn.addEventListener('click', async () => {
    const response = await fetch(`/case/delete/${screenshot.id}/screenshot`, {
      method: 'DELETE',
    });
    if (response.status == 200) {
      screenshotDiv.remove();
    }
  });

  return screenshotDiv;
};

const editCase = async (caseId: number) => {
  const title: HTMLInputElement = document.querySelector('#edit-case-title');
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
  const isMain: HTMLInputElement = document.querySelector('#edit-case-is-main');
  const stacks = document.querySelectorAll('#stacks input[type="checkbox"]');
  const mainImage: HTMLImageElement = document.querySelector(
    '#edit-case-main-image',
  );
  const previewImage: HTMLImageElement = document.querySelector(
    '#edit-case-preview-image',
  );
  const divCaseScreenShoots = document.querySelector('#edit-case-screenshots');
  const caseIdElement: HTMLInputElement = document.querySelector('#caseIdEdit');

  const mainImageInput: HTMLInputElement = document.querySelector(
    '#edit-case-main-image-input',
  );
  const subMainImageInput: HTMLInputElement = document.querySelector(
    '#edit-case-sub-main-image-input',
  );

  if (
    !title ||
    !subTitle ||
    !description ||
    !role ||
    !isActive ||
    !isMain ||
    !caseIdElement ||
    !mainImage ||
    !previewImage ||
    !divCaseScreenShoots ||
    !mainImageInput ||
    !subMainImageInput
  ) {
    return;
  }

  const response = await fetch(`/case/${caseId}`, {
    method: 'GET',
  });
  const caseData: ICaseOut = await response.json();

  const listOfScreenshots: ICaseScreenshot[] = caseData.screenshots;

  listOfScreenshots.forEach((screenshot: ICaseScreenshot) => {
    divCaseScreenShoots.appendChild(createCaseScreenshot(screenshot));
  });

  stacks.forEach((checkbox: HTMLInputElement) => {
    const label = checkbox.nextElementSibling.textContent;

    if (caseData.stacks_names.includes(label)) {
      checkbox.checked = true;
    }
  });

  title.value = caseData.title;
  subTitle.value = caseData.sub_title;
  description.value = caseData.description;
  role.value = caseData.role;
  isActive.checked = caseData.is_active;
  isMain.checked = caseData.is_main;
  mainImage.src =
    mainImageInput.files.length > 0
      ? URL.createObjectURL(mainImageInput.files[0])
      : caseData.main_image_url;
  previewImage.src =
    subMainImageInput.files.length > 0
      ? URL.createObjectURL(subMainImageInput.files[0])
      : caseData.preview_image_url;

  caseIdElement.setAttribute('value', caseId.toString());

  mainImageInput.addEventListener('change', () => {
    const files = mainImageInput.files;
    if (files.length > 0) {
      mainImage.src = URL.createObjectURL(files[0]);
    }
  });

  subMainImageInput.addEventListener('change', () => {
    const files = subMainImageInput.files;
    if (files.length > 0) {
      previewImage.src = URL.createObjectURL(files[0]);
    }
  });
};

export const cases = () => {
  const $addUserModalElement: HTMLElement =
    document.querySelector('#addCaseModal');
  const $stackModalElement: HTMLElement = document.querySelector('#stackModal');
  const scrfInput: HTMLInputElement = document.querySelector('#csrf_token');

  const $caseEditModalElement: HTMLElement = document.querySelector(
    '#caseEditModalElement',
  );

  const {openModal} = useConfirmModal();

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

  // callBack on btn is_active and is_main
  const caseConfirmModalListener = (
    event: MouseEvent,
    inputElement: HTMLInputElement,
  ) => {
    event.preventDefault();
    const caseId = inputElement.getAttribute('data-case-id');
    const caseStatusAtr = inputElement.getAttribute('data-case-status');
    const dataFiled = inputElement.getAttribute('data-field');

    const isCaseActive = caseStatusAtr === 'True';
    let caseConfirmModalText;
    const text = 'Are you sure you want to';
    if (dataFiled === 'is_active') {
      caseConfirmModalText = isCaseActive
        ? `${text} deactivate case ${caseId}`
        : `${text} activate case ${caseId}`;
    } else if (dataFiled === 'is_main') {
      caseConfirmModalText = isCaseActive
        ? `${text} deactivate main case ${caseId}`
        : `${text} activate main case ${caseId}`;
    }

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

    openModal(caseConfirmModalText, confirmCallback);
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
        const caseId = e.getAttribute('data-case-id');
        const modalText = `Are you sure you want to delete case ${caseId}?`;

        const confirmCallback = async () => {
          const response = await fetch(`/case/delete/${caseId}`, {
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
  const editCaseButton = document.querySelectorAll('#edit-case-btn');

  editCaseButton.forEach(e => {
    e.addEventListener('click', async () => {
      editCaseModal.show();

      const caseId = e.getAttribute('data-edit-id');

      await editCase(Number(caseId));

      const editModalCloseBtn = document.querySelector('#editCaseModalClose');
      const divCaseScreenShoots = document.querySelector(
        '#edit-case-screenshots',
      );

      if (editModalCloseBtn) {
        editModalCloseBtn.addEventListener('click', () => {
          if (divCaseScreenShoots) {
            while (divCaseScreenShoots.firstChild) {
              divCaseScreenShoots.removeChild(divCaseScreenShoots.firstChild);
            }
          }
          editCaseModal.hide();
        });
      }
    });
  });
};
