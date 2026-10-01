// 1. Ambil form dari HTML berdasarkan id-nya
const form = document.getElementById("formRegister");

// 2. Fungsi kecil untuk menampilkan pesan error
function tampilkanError(idError, pesan) {
  document.getElementById(idError).textContent = pesan;
}

// 3. Fungsi untuk menghapus semua pesan error lama
function hapusSemuaError() {
  const daftarId = [
    "errorUsername", "errorPassword", "errorNama",
    "errorTanggalLahir", "errorAlamat", "errorTelepon"
  ];
  daftarId.forEach(function (id) {
    document.getElementById(id).textContent = "";
  });
}

// 4. Pasang event "submit" pada form
form.addEventListener("submit", function (event) {
  // Anggap dulu semuanya benar
  let valid = true;

  // Bersihkan pesan error dari pengecekan sebelumnya
  hapusSemuaError();

  // Ambil isi setiap kolom (.trim() membuang spasi di awal & akhir)
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const nama = document.getElementById("nama").value.trim();
  const tanggalLahir = document.getElementById("tanggalLahir").value;
  const alamat = document.getElementById("alamat").value.trim();
  const telepon = document.getElementById("telepon").value.trim();

  // a. Username: tidak kosong, minimal 3 karakter
  if (username === "") {
    tampilkanError("errorUsername", "Username tidak boleh kosong");
    valid = false;
  } else if (username.length < 3) {
    tampilkanError("errorUsername", "Username minimal 3 karakter");
    valid = false;
  }

  // b. Password: tidak kosong, minimal 8 karakter
  if (password === "") {
    tampilkanError("errorPassword", "Password tidak boleh kosong");
    valid = false;
  } else if (password.length < 8) {
    tampilkanError("errorPassword", "Password minimal 8 karakter");
    valid = false;
  }

  // c. Nama: tidak kosong
  if (nama === "") {
    tampilkanError("errorNama", "Nama tidak boleh kosong");
    valid = false;
  }

  // d. Tanggal lahir: tidak kosong, tidak boleh tanggal masa depan
  if (tanggalLahir === "") {
    tampilkanError("errorTanggalLahir", "Tanggal lahir tidak boleh kosong");
    valid = false;
  } else {
    const hariIni = new Date();
    hariIni.setHours(0, 0, 0, 0); // set jam ke 00:00 supaya yang dibandingkan hanya tanggalnya

    const tglLahir = new Date(tanggalLahir + "T00:00:00");

    if (tglLahir > hariIni) {
      tampilkanError("errorTanggalLahir", "Tanggal lahir tidak boleh melebihi hari ini");
      valid = false;
    }
  }

  // e. Alamat: tidak kosong
  if (alamat === "") {
    tampilkanError("errorAlamat", "Alamat tidak boleh kosong");
    valid = false;
  }

  // f. Nomor telepon: "+62" sudah ada di kotak terpisah, user hanya mengisi sisanya
  if (telepon === "") {
    tampilkanError("errorTelepon", "Nomor telepon tidak boleh kosong");
    valid = false;
  } else if (!/^[0-9]+$/.test(telepon)) {
    tampilkanError("errorTelepon", "Nomor telepon hanya boleh berisi angka");
    valid = false;
  } else if (telepon.startsWith("0")) {
    tampilkanError("errorTelepon", "Jangan diawali 0, contoh: 81234567890");
    valid = false;
  } else {
    // Gabungkan 62 + nomor, lalu simpan di kotak tersembunyi
    document.getElementById("teleponLengkap").value = "62" + telepon;
  }

  // 5. Kalau ada yang salah, BATALKAN pengiriman form
  if (valid === false) {
    event.preventDefault();
  }
});
