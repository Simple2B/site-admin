import { Modal } from 'flowbite';
import type { ModalOptions, ModalInterface } from 'flowbite';

export const stack = () => {
  const form = document.getElementById('add-stack-form') as HTMLFormElement;
  const inputElement = document.getElementById('add-stack-form-input') as HTMLInputElement;
  const stacksDiv = document.getElementById('add-stack-form-stacks');
  const scrfInput: HTMLInputElement =
    document.querySelector('#csrf_token');

  let oldSpansName: string[];

  if (stacksDiv) {
    oldSpansName = Array.from(stacksDiv.querySelectorAll('span')).map((span) => span.textContent);
  }

  const listElementsCases = document.getElementById('listOfCases');
  const $deleteStackModal: HTMLElement =
    document.querySelector('#deleteStackModal');

  const modalOptions: ModalOptions = {
    backdrop: 'static',
    closable: true,
    onHide: () => { },
    onShow: () => { },
    onToggle: () => { },
  };

  let stackModalWarning: ModalInterface;

  if ($deleteStackModal) {
    stackModalWarning = new Modal(
      $deleteStackModal,
      modalOptions
    )
  }

  const stackModalCloseBtn = document.querySelector(
    '#modalStackCloseButtonError',
  );
  if (stackModalCloseBtn) {
    stackModalCloseBtn.addEventListener('click', () => {
      stackModalWarning.hide();
    });
  }

  // This selects elements where the id attribute starts with the string "button-"
  const listOfStacks = document.querySelectorAll('[id^="button-"]');

  if (listOfStacks) {
    listOfStacks.forEach(button => {
      const stackName = button.id.replace("button-", "");
      button.addEventListener("click", async () => {

        const formData = new FormData();
        formData.append('stacks', stackName);

        const response = await fetch(`/stack/delete`, {
          method: 'DELETE',
          body: formData,
        });

        if (response.status === 422 && listElementsCases) {
          const stringList = await response.json();

          // Clear existing content
          listElementsCases.innerHTML = '';

          // Create a <span> element for each string and append it to the container
          stringList.forEach((item: string) => {

            const span = document.createElement('span');
            const lineBreak = document.createElement('br');

            span.textContent = item;
            span.setAttribute("class", "font-semibold text-xl");
            listElementsCases.appendChild(span);
            listElementsCases.appendChild(lineBreak);
          });

          stackModalWarning.show();
        }

        if (response.status == 200) {
          location.reload();
        }
      });
    });
  }

  if (form) {
    form.onkeydown = function (e) {
      if (e.key === 'Enter' && inputElement.value && stacksDiv) {
        e.preventDefault();

        const newStack = document.createElement('span');

        newStack.textContent = inputElement.value
        newStack.setAttribute("class", "bg-indigo-200 text-indigo-800 text-lg font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-indigo-400 border border-indigo-400")

        const newSpansName = Array.from(stacksDiv.querySelectorAll('span')).map((span) => span.textContent);

        if (!oldSpansName.includes(inputElement.value) && !newSpansName.includes(inputElement.value)) {
          stacksDiv.appendChild(newStack);
        }

        inputElement.value = ""
      }
    }
  };

  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (stacksDiv) {
      const newStacks = Array.from(
        stacksDiv.querySelectorAll('span')
      ).map((span) => span.textContent
      ).filter((stack) => !oldSpansName.includes(stack))

      if (inputElement && inputElement.value && !newStacks.includes(inputElement.value)) {
        newStacks.push(inputElement.value)
      }

      const fetchStr = newStacks.join(',');

      if (fetchStr) {
        const formData = new FormData();
        formData.append('stacks', fetchStr);
        formData.append("csrf_token", scrfInput ? scrfInput.value : '',)

        const response = await fetch(`/stack/create`, {
          method: 'POST',
          body: formData,
        });

        if (response.status == 200) {
          location.reload();
          inputElement.value = ""
        }
      }
    }
  }

  if (form) {
    form.addEventListener('submit', handleSubmit);
  }
}
