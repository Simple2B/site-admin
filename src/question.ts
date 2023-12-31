import {Modal} from 'flowbite';
import type {ModalOptions, ModalInterface} from 'flowbite';
import {modalOptions, useConfirmModal} from './utils';

export const questions = () => {
  const $addQuestionModalElement: HTMLElement =
    document.querySelector('#addQuestionModal');
  const $editQuestionModalElement: HTMLElement =
    document.querySelector('#editQuestionModal');

  const {openModal} = useConfirmModal();

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
        const questionId = e.getAttribute('data-question-id');
        const modalText = `Are you sure you want to delete question ${questionId}?`;

        const confirmCallback = async () => {
          const response = await fetch(`/quiz/delete/${questionId}`, {
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
        const questionText: HTMLTextAreaElement =
          document.querySelector('#question-text');
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
        const selectOptions: NodeListOf<HTMLOptionElement> =
          document.querySelectorAll('[id^="select_option"]');
        const questionTitle = document.querySelector('#question-title');
        if (
          data &&
          questionText &&
          questionVariantOne &&
          questionVariantTwo &&
          questionVariantThree &&
          questionVariantFour &&
          questionCorrectAnswerMark &&
          questionId &&
          questionUuid &&
          questionTitle
        ) {
          questionId.setAttribute('value', data.id);
          questionUuid.setAttribute('value', data.uuid);
          questionTitle.textContent = `Question: ${data.id}`;
          questionText.value = data.text;
          questionVariantOne.setAttribute('value', data.variants[0].text);
          questionVariantTwo.setAttribute('value', data.variants[1].text);
          questionVariantThree.setAttribute('value', data.variants[2].text);
          questionVariantFour.setAttribute('value', data.variants[3].text);
          selectOptions.forEach((opt, index) => {
            opt.textContent = `${index + 1}: ${data.variants[index].text}`;
            opt.value = `${index + 1}`;
          });
          selectedOption.setAttribute('selected', 'true');
        }
      });
    });
  }
};
