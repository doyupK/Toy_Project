// 김민수 : 회원 가입 및 관리 기능 =================================================================================

var checkIdResult = false
var checkIdDuplicationResult = false
var checkPasswordResult = false
var checkPasswordConfirmResult = false
var checkNameResult = false
var checkEmailResult = false
var checkAddressResult = false

// 아이디 조합 체크
function checkId(id) { // 아이디 입력값 검증
    checkIdDuplicationResult = false
    var regex = new RegExp(/^[A-Za-z0-9]{4,12}$/); // 4~12자리 영문,숫자 조합 정규 표현식 활용
    var element = document.getElementById('checkIdResult');
    if (regex.exec(id)) {
        element.innerHTML = '사용 가능';
        element.style.color = 'green';
        checkIdResult = true; // 전역변수값을 true 로 변경
    } else {
        element.innerHTML = '사용 불가능';
        element.style.color = 'red';
        checkIdResult = false; // 전역변수값을 false 로 변경
    }
}

// 비밀번호 조합 체크
function checkPassword(password) {
    var lengthRegex = /^[A-Za-z0-9!@#$%]{8,16}$/;
    var engUpperCaseRegex = /[A-Z]/;
    var engLowerCaseRegex = /[a-z]/;
    var digitRegex = /[0-9]/;
    var specRegex = /[!@#$%]/;
    var element = document.getElementById('checkPasswordResult');
    if (lengthRegex.exec(password)) {
        var safetyCount = 0;
        if (engUpperCaseRegex.exec(password)) safetyCount++;
        if (engLowerCaseRegex.exec(password)) safetyCount++;
        if (digitRegex.exec(password)) safetyCount++;
        if (specRegex.exec(password)) safetyCount++;

        switch (safetyCount) {
            case 4:
                element.innerHTML = '매우 안전';
                element.style.color = 'green';
                checkPasswordResult = true; // 전역변수값을 true 로 변경
                break;
            case 3:
                element.innerHTML = '안전';
                element.style.color = 'yellow';
                checkPasswordResult = true; // 전역변수값을 true 로 변경
                break;
            case 2:
                element.innerHTML = '보통';
                element.style.color = 'orange';
                checkPasswordResult = true; // 전역변수값을 true 로 변경
                break;
            case 1:
                element.innerHTML = '사용불가';
                element.style.color = 'red';
                checkPasswordResult = false; // 전역변수값을 false 로 변경
                break;
        }
    } else {
        element.innerHTML = '영문자,숫자,특수문자 초쇠 2가지 조합 필수!';
        element.style.color = 'red';
        checkPasswordResult = false; // 전역변수값을 false 로 변경
    }
}

function checkPasswordConfirm(password) { // 패스워드 일치 확인
    var element = document.getElementById('passwordConfirmResult');
    if (password == $('#floatingInput_PW').val()) { // 패스워드 확인 내용 일치 시
        element.innerHTML = '패스워드 일치';
        element.style.color = 'green';
        checkPasswordConfirmResult = true; // 전역변수값을 true 로 변경
    } else {
        element.innerHTML = '패스워드 불일치';
        element.style.color = 'red';
        checkPasswordConfirmResult = false; // 전역변수값을 false 로 변경
    }
}

// 회원 가입
function users_signUp() {
    let id = $('#floatingInput_ID').val()
    let password = $('#floatingInput_PW').val()
    let name = $('#floatingInput_name').val()
    let email = $('#floatingInput_Email').val()
    let address = $('#floatingInput_address').val()

    if (name != '') {
        checkNameResult = true
    }
    if (email != '') {
        checkEmailResult = true
    }
    if (address != '') {
        checkAddressResult = true
    }

    switch (false) {
        case checkIdResult:
            alert('아이디를 확인하세요');
            return;
        case checkIdDuplicationResult:
            alert('아이디 중복확인 필수 입니다');
            return;
        case checkPasswordResult:
            alert('비밀번호를 확인하세요');
            return;
        case checkPasswordConfirmResult:
            alert('비밀번호가 일치하지 않습니다');
            return;
        case checkNameResult:
            alert('이름을 입력하세요');
            return;
        case checkEmailResult:
            alert('이메일을 입력하세요');
            return;
        case checkAddressResult:
            alert('주소를 입력하세요');
            return;
        default:
            $.ajax({
                type: 'POST',
                url: '/users_signup',
                data: {
                    id_give: id,
                    pw_give: password,
                    name_give: name,
                    email_give: email,
                    address_give: address
                },
                success: function (response) {
                    alert(response['msg'])
                    window.location.href = "/"
                }
            });
    }
}

// 아이디 중복체크
function users_idCheck() {
    let id = $('#floatingInput_ID').val()
    $.ajax({
        type: "GET",
        url: "/users_idCheck",
        data: {id_give: id},
        success: function (response) {
            if (response['user']) {
                checkIdDuplicationResult = true
                alert("사용가능한 아이디 입니다.")
            } else {
                checkIdDuplicationResult = false
                alert("사용할수 없습니다.")
            }
        }
    })
}

// 주소 찾기 다음 api
var element_layer = document.getElementById('layer');// 우편번호 찾기 화면을 넣을 element
function closeDaumPostcode() {
    // iframe을 넣은 element를 안보이게 한다.
    element_layer.style.display = 'none';
}

function address_find() {
    new daum.Postcode({
        oncomplete: function (data) {
            var addr = ''; // 주소 변수
            var extraAddr = ''; // 참고항목 변수
            //사용자가 선택한 주소 타입에 따라 해당 주소 값을 가져온다.
            if (data.userSelectedType === 'R') { // 사용자가 도로명 주소를 선택했을 경우
                addr = data.roadAddress;
            } else { // 사용자가 지번 주소를 선택했을 경우(J)
                addr = data.jibunAddress;
            }

            // 사용자가 선택한 주소가 도로명 타입일때 참고항목을 조합한다.
            if (data.userSelectedType === 'R') {
                // 법정동명이 있을 경우 추가한다. (법정리는 제외)
                // 법정동의 경우 마지막 문자가 "동/로/가"로 끝난다.
                if (data.bname !== '' && /[동|로|가]$/g.test(data.bname)) {
                    extraAddr += data.bname;
                }
                // 건물명이 있고, 공동주택일 경우 추가한다.
                if (data.buildingName !== '' && data.apartment === 'Y') {
                    extraAddr += (extraAddr !== '' ? ', ' + data.buildingName : data.buildingName);
                }
                // 표시할 참고항목이 있을 경우, 괄호까지 추가한 최종 문자열을 만든다.
                if (extraAddr !== '') {
                    extraAddr = ' (' + extraAddr + ')';
                }
                // 조합된 참고항목을 해당 필드에 넣는다.
                // document.getElementById("sample2_extraAddress").value = extraAddr;
                document.getElementById("floatingInput_address").value = addr + extraAddr;

            } else {
                // document.getElementById("sample2_extraAddress").value = '';
                document.getElementById("floatingInput_address").value = addr + extraAddr;
            }

            // 우편번호와 주소 정보를 해당 필드에 넣는다.
            // document.getElementById('sample2_postcode').value = data.zonecode;
            // document.getElementById("sample2_address").value = addr;
            // 커서를 상세주소 필드로 이동한다.
            // document.getElementById("sample2_detailAddress").focus();

            // iframe을 넣은 element를 안보이게 한다.
            // (autoClose:false 기능을 이용한다면, 아래 코드를 제거해야 화면에서 사라지지 않는다.)
            element_layer.style.display = 'none';
        },
        width: '100%',
        height: '100%',
        maxSuggestItems: 5
    }).embed(element_layer);

    // iframe을 넣은 element를 보이게 한다.
    element_layer.style.display = 'block';

    // iframe을 넣은 element의 위치를 화면의 가운데로 이동시킨다.
    initLayerPosition();
}

function initLayerPosition() {
    // 브라우저의 크기 변경에 따라 레이어를 가운데로 이동시키고자 하실때에는
    // resize이벤트나, orientationchange이벤트를 이용하여 값이 변경될때마다 아래 함수를 실행 시켜 주시거나,
    // 직접 element_layer의 top,left값을 수정해 주시면 됩니다.
    var width = 300; //우편번호서비스가 들어갈 element의 width
    var height = 400; //우편번호서비스가 들어갈 element의 height
    var borderWidth = 5; //샘플에서 사용하는 border의 두께

    // 위에서 선언한 값들을 실제 element에 넣는다.
    element_layer.style.width = width + 'px';
    element_layer.style.height = height + 'px';
    element_layer.style.border = borderWidth + 'px solid';
    // 실행되는 순간의 화면 너비와 높이 값을 가져와서 중앙에 뜰 수 있도록 위치를 계산한다.
    element_layer.style.left = (((window.innerWidth || document.documentElement.clientWidth) - width) / 2 - borderWidth) + 'px';
    element_layer.style.top = (((window.innerHeight || document.documentElement.clientHeight) - height) / 2 - borderWidth) + 'px';
}


// 회원 정보 변경
function users_update() {
    let id = $('#floatingInput_ID').val()
    let password = $('#floatingInput_PW').val()
    let passwordCheck = $('#floatingInput_PW_Check').val()
    let email = $('#floatingInput_Email').val()
    let address = $('#floatingInput_address').val()
    if (email != '') {
        checkEmailResult = true
    }
    if (address != '') {
        checkAddressResult = true
    }
    if (password != passwordCheck) {
        checkPasswordConfirmResult = false
    }

    switch (false) {
        case checkPasswordResult:
            alert('비밀번호를 확인하세요');
            return;
        case checkPasswordConfirmResult:
            alert('비밀번호가 일치하지 않습니다');
            return;
        case checkEmailResult:
            alert('이메일을 입력하세요');
            return;
        case checkAddressResult:
            alert('주소를 입력하세요');
            return;
        default:
            $.ajax({
                type: 'POST',
                url: '/users_update',
                data: {
                    id_give: id, pw_give: password, email_give: email, address_give: address
                },
                success: function (response) {
                    alert(response['msg'])
                    window.location.href = "/"
                }
            });
    }
}

// 회원 정보 삭제
function users_delete() {
    let id = $('#floatingInput_ID').val()
    $.ajax({
        type: 'POST',
        url: '/users_delete',
        data: {id_give: id},
        success: function (response) {
            $.removeCookie('mytoken', {path: '/'});
            alert(response['msg'])
            window.location.href = "/"
        }
    });
}



// 김민수 : 회원 가입 및 관리 기능 =================================================================================

