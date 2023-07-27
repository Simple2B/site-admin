import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';

export const questions = () => {
  const $addQuestionModalElement: HTMLElement =
    document.querySelector('#addQuestionModal');
  const $editQuestionModalElement: HTMLElement =
    document.querySelector('#editQuestionModal');

  const modalOptions: ModalOptions = {
    backdrop: 'static',
    closable: true,
    onHide: () => {},
    onShow: () => {},
    onToggle: () => {},
  };

  const addQuestionModal: ModalInterface = new Modal(
    $addQuestionModalElement,
    modalOptions,
  );
  const editQuestionModal: ModalInterface = new Modal(
    $editQuestionModalElement,
    modalOptions,
  );

  // opening add user modal
  const addQuestionButton = document.querySelector('#add-question-btn');
  if (addQuestionButton) {
    addQuestionButton.addEventListener('click', () => {
      addQuestionModal.show();
    });

    // closing add user modal
    const addModalCloseBtn = document.querySelector(
      '#modalAddQuestionCloseButton',
    );
    if (addModalCloseBtn) {
      addModalCloseBtn.addEventListener('click', () => {
        addQuestionModal.hide();
      });
    }

    // // search flow
    const searchInput: HTMLInputElement = document.querySelector(
      '#table-search-question',
    );
    const searchInputButton = document.querySelector(
      '#table-search-question-button',
    );
    if (searchInputButton && searchInput) {
      searchInputButton.addEventListener('click', () => {
        const url = new URL(window.location.href);
        url.searchParams.set('q', searchInput.value);
        window.location.href = `${url.href}`;
      });
    }
    const deleteButtons = document.querySelectorAll('.delete-question-btn');

    deleteButtons.forEach(e => {
      e.addEventListener('click', async () => {
        if (confirm('Are sure?')) {
          let id = e.getAttribute('data-question-id');
          const response = await fetch(`/quiz/delete/${id}`, {
            method: 'DELETE',
          });
          if (response.status == 200) {
            location.reload();
          }
        }
      });
    });
  }
  const editQuestionButton = document.querySelectorAll('#edit-question-btn');
  if (editQuestionButton) {
    editQuestionButton.forEach(btn => {
      btn.addEventListener('click', async () => {
        editQuestionModal.show();
        let id = btn.getAttribute('data-question-id');
        const response = await fetch(`/quiz/get/${id}`, {
          method: 'GET',
        });
        const data = await response.json();
        const questionId: HTMLInputElement = document.querySelector('#id');
        const questionUuid: HTMLInputElement = document.querySelector('#uuid');
        const questionText = document.querySelector('#question-text');
        const questionVariantOne: HTMLInputElement = document.querySelector(
          '#question-variant-one',
        );
        const questionVariantTwo: HTMLInputElement = document.querySelector(
          '#question-variant-two',
        );
        const questionVariantThree: HTMLInputElement = document.querySelector(
          '#question-variant-three',
        );
        const questionVariantFour: HTMLInputElement = document.querySelector(
          '#question-variant-four',
        );
        const questionCorrectAnswerMark: HTMLSelectElement =
          document.querySelector('#correct_answer_mark');
        const selectedOption = document.querySelector(
          `#select_option_${data.correct_answer_mark}`,
        );
        if (
          data &&
          questionText &&
          questionVariantOne &&
          questionVariantTwo &&
          questionVariantThree &&
          questionVariantFour &&
          questionCorrectAnswerMark &&
          questionId &&
          questionUuid
        ) {
          questionId.setAttribute('value', data.id);
          questionUuid.setAttribute('value', data.uuid);
          questionText.setAttribute('value', data.text);
          questionVariantOne.setAttribute('value', data.variants[0].text);
          questionVariantTwo.setAttribute('value', data.variants[1].text);
          questionVariantThree.setAttribute('value', data.variants[2].text);
          questionVariantFour.setAttribute('value', data.variants[3].text);
          selectedOption.setAttribute('selected', 'true');
        }
      });
    });

    // closing add user modal
    const editModalCloseBtn = document.querySelector(
      '#modalEditQuestionCloseButton',
    );
    if (editModalCloseBtn) {
      editModalCloseBtn.addEventListener('click', () => {
        editQuestionModal.hide();
      });
    }
  }
};
