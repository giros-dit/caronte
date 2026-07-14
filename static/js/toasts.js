document.body.addEventListener('htmx:beforeOnLoad', function (evt) {
    if (evt.detail.xhr.status >= 400 && evt.detail.xhr.status < 600) {
        evt.detail.shouldSwap = true;
        evt.detail.isError = false;
    }
});

toastr.options = {
  "closeButton": true,
  "debug": false,
  "newestOnTop": false,
  "progressBar": true,
  "positionClass": "toast-bottom-right",
  "preventDuplicates": false,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
}

document.body.addEventListener('new-toast', (event) => { 
    const toastData = event.detail.value || event.detail;

    if (Array.isArray(toastData)) {
        toastData.forEach(toast => launchToast(toast));
    } else {
        launchToast(toastData);
    }
});

function launchToast(data) {
    if (data && typeof toastr[data.type] === 'function') {
        toastr[data.type](data.message, data.title, data.options);
    } else {
        console.error('Tipo de toastr no válido o datos incompletos:', data);
    }
}


document.body.addEventListener('clear-toasts', (event) => {
    toastr.clear();
})