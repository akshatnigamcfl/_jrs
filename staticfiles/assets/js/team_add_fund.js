function teamAddFund(heading){
    const div = document.createElement('div');
    div.classList = 'w-screen h-screen bg-[rgba(0,0,0,0.5)] absolute flex justify-center items-center z-50';
    div.innerHTML = `
    <div class="w-full flex justify-center">
    <div class="w-96 border p-3 rounded-2xl flex items-center flex-col bg-white py-4 px-8 relative">
    <span class="font-bold my-4 text-lg select-none capitalize">${heading}</span>

    <div class="flex w-full">
        <label class="w-1/4">Amount</label>
        <input type="number" class="amount outline-0 text-slate-900 px-2 border rounded-lg w-3/4 h-8 my-1 ml-3">
    </div>

    <div class="flex w-full booking_main_div relative">
        <label class="w-1/4">Booking</label>
        <input class="booking outline-0 text-slate-900 px-2 border rounded-lg w-3/4 h-8 my-1 ml-3">
        <input type="number" class="booking_id hidden">
    </div>

    <div class="flex w-full">
        <label class="w-1/4">Notes</label>
        <input class="notes outline-0 text-slate-900 px-2 border rounded-lg w-3/4 h-12 my-1 ml-3">
    </div>
    
    <div class="w-full flex justify-center my-4">
        <button class="save btn btn-sm btn-success text-white">Save</button>
        <button class="close_btn btn btn-sm btn-ghost text-slate-900">Cancel</button></div>
    </div>
    </div>
    `
    // <img class=" close_btn absolute right-[10px] top-[10px] h-[20px] w-[20px] hover:h-[21px] hover:w-[21px] duration-200" src="/static/assets/images/icons/close_button_black.png">
  document.body.prepend(div);
  
  const close_btn = document.querySelector('.close_btn');
  close_btn.addEventListener('click',()=>{
      div.remove()
    })

document.addEventListener('keyup', (e)=>{
    if (e.key == 'Escape'){
      popup_check = false;
      div.remove()
    }
})

}