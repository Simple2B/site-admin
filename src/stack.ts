export const stack = () => {
  const form = document.getElementById('add-stack-form') as HTMLFormElement;
  const name = document.getElementById(
    'add-stack-form-input',
  ) as HTMLInputElement;
  const stacksDiv = document.getElementById('add-stack-form-stacks');
  const scrfInput: HTMLInputElement = document.querySelector('#csrf_token');
  if (!form || !name || !stacksDiv) {
    return;
  }
  const oldSpansName = Array.from(stacksDiv.querySelectorAll('span')).map(
    span => span.textContent,
  );

  form.onkeydown = function (e) {
    if (e.keyCode == 13 && name.value && stacksDiv) {
      e.preventDefault();
      const newStack = document.createElement('span');
      newStack.textContent = name.value;
      newStack.setAttribute(
        'class',
        'bg-indigo-100 text-indigo-800 text-lg font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-gray-700 dark:text-indigo-400 border border-indigo-400',
      );
      const newSpansName = Array.from(stacksDiv.querySelectorAll('span')).map(
        span => span.textContent,
      );
      if (
        !oldSpansName.includes(name.value) &&
        !newSpansName.includes(name.value)
      ) {
        stacksDiv.appendChild(newStack);
      }
      name.value = '';
    }
  };

  async function handleSubmit(event: Event) {
    event.preventDefault();
    const newStacks = Array.from(stacksDiv.querySelectorAll('span'))
      .map(span => span.textContent)
      .filter(stack => !oldSpansName.includes(stack));

    if (name && name.value && !newStacks.includes(name.value)) {
      newStacks.push(name.value);
    }

    const fetchStr = newStacks.join(',');
    if (fetchStr) {
      const formData = new FormData();
      formData.append('stacks', fetchStr);
      formData.append('csrf_token', scrfInput ? scrfInput.value : '');
      const response = await fetch(`/stack/create`, {
        method: 'POST',
        body: formData,
      });
      if (response.status == 200) {
        location.reload();
        name.value = '';
      }
    }
  }
  form.addEventListener('submit', handleSubmit);
};
