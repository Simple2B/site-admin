import { Modal } from 'flowbite';
import type { ModalOptions, ModalInterface } from 'flowbite';

export const cases = () => {
  const $addUserModalElement: HTMLElement =
    document.querySelector('#addCaseModal');
  const $stackModalElement: HTMLElement =
    document.querySelector('#stackModal');
  const scrfInput: HTMLInputElement =
    document.querySelector('#csrf_token');

  const $caseEditModalElement: HTMLElement =
    document.querySelector('#caseEditModalElement');

  const modalOptions: ModalOptions = {
    backdrop: 'static',
    closable: true,
    onHide: () => { },
    onShow: () => { },
    onToggle: () => { },
  };

  const addModal: ModalInterface = new Modal(
    $addUserModalElement,
    modalOptions,
  );

  const stackModal: ModalInterface = new Modal(
    $stackModalElement,
    modalOptions
  )

  const editCaseModal: ModalInterface = new Modal(
    $caseEditModalElement,
    modalOptions
  )

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
  const editCaseButton = document.querySelectorAll('#edit-case-btn');

  console.log(editCaseButton);

  editCaseButton.forEach(e => {
    e.addEventListener('click', async () => {
      editCaseModal.show();

      const caseId = e.getAttribute('data-edit-id');

      console.log(caseId);

      const response = await fetch(`/case/get/${caseId}`, {
        method: 'GET',
      });
      const caseData = await response.json();
      console.log(caseData._stacks.map((stack: any) => stack.name));

      const listOfStacks = caseData._stacks.map((stack: any) => stack.name);

      //TODO add check for elements
      const title: HTMLInputElement = document.querySelector('#edit-case-title');
      const subTitle: HTMLInputElement = document.querySelector('#edit-case-sub-title');
      const description: HTMLInputElement = document.querySelector('#edit-case-description');
      const role: HTMLInputElement = document.querySelector('#edit-case-role');
      const isActive: HTMLInputElement = document.querySelector('#edit-case-is-active');
      const isMain: HTMLInputElement = document.querySelector('#edit-case-is-main');
      const stacks = document.querySelectorAll('#stacks input[type="checkbox"]');

      const caseIdElement: HTMLInputElement = document.querySelector('#caseIdEdit');

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

      caseIdElement.setAttribute('value', caseId);

      const editModalCloseBtn = document.querySelector(
        '#editCaseModalClose',
      );

      if (editModalCloseBtn) {
        editModalCloseBtn.addEventListener('click', () => {
          editCaseModal.hide();
        });
      }
    });
  });
};
