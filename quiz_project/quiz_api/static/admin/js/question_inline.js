// 質問インライン管理のJavaScript
(function($) {
    'use strict';
    
    $(document).ready(function() {
        
        // 正解チェックボックスの排他制御
        function setupCorrectAnswerExclusive() {
            $(document).on('change', 'input[id$="_correct"]', function() {
                if (this.checked) {
                    // 同じ質問内の他の正解チェックボックスを無効化
                    var $container = $(this).closest('.inline-group');
                    $container.find('input[id$="_correct"]').not(this).prop('checked', false);
                    
                    // ハイライト更新
                    updateCorrectChoiceHighlight($container);
                }
                validateQuestion($(this).closest('.inline-group'));
            });
        }
        
        // 正解選択肢のハイライト更新
        function updateCorrectChoiceHighlight($container) {
            $container.find('.form-row').removeClass('correct-choice');
            $container.find('input[id$="_correct"]:checked').each(function() {
                $(this).closest('.form-row').addClass('correct-choice');
            });
        }
        
        // 質問バリデーション
        function validateQuestion($container) {
            var correctCount = $container.find('input[id$="_correct"]:checked').length;
            var choiceCount = 0;
            
            // 入力された選択肢をカウント
            for (var i = 1; i <= 6; i++) {
                var text = $container.find('input[id$="choice' + i + '_text"]').val();
                if (text && text.trim()) {
                    choiceCount++;
                }
            }
            
            // バリデーションメッセージをクリア
            $container.find('.validation-message').remove();
            
            var messages = [];
            
            if (choiceCount < 2) {
                messages.push({
                    type: 'error',
                    text: 'エラー: 最低2つの選択肢が必要です'
                });
            }
            
            if (correctCount === 0 && choiceCount >= 2) {
                messages.push({
                    type: 'warning',
                    text: '警告: 正解が選択されていません'
                });
            } else if (correctCount > 1) {
                messages.push({
                    type: 'error',
                    text: 'エラー: 正解は1つだけ選択してください'
                });
            } else if (correctCount === 1) {
                messages.push({
                    type: 'success',
                    text: '✓ 正しく設定されています'
                });
            }
            
            // メッセージを表示
            messages.forEach(function(msg) {
                var $message = $('<div class="validation-message ' + msg.type + '">' + msg.text + '</div>');
                $container.find('h2').after($message);
            });
        }
        
        // 選択肢テキストの変更を監視
        function setupTextFieldValidation() {
            $(document).on('input', 'input[id$="_text"]', function() {
                var $container = $(this).closest('.inline-group');
                validateQuestion($container);
                updateChoiceNumbering($container);
            });
        }
        
        // 選択肢の自動番号付け
        function updateChoiceNumbering($container) {
            for (var i = 1; i <= 6; i++) {
                var $textField = $container.find('input[id$="choice' + i + '_text"]');
                $textField.attr('placeholder', i + '. 選択肢を入力してください...');
            }
        }
        
        // 折りたたみ機能
        function setupCollapsible() {
            $('.collapse h3').addClass('collapse-toggle collapsed').on('click', function() {
                var $section = $(this).parent();
                var $content = $section.find('.form-row');
                
                if ($(this).hasClass('collapsed')) {
                    $content.slideDown(300);
                    $(this).removeClass('collapsed');
                } else {
                    $content.slideUp(300);
                    $(this).addClass('collapsed');
                }
            });
            
            // 初期状態で折りたたみ
            $('.collapse .form-row').hide();
        }
        
        // フォーム送信前のバリデーション
        function setupFormValidation() {
            $('form').on('submit', function(e) {
                var hasErrors = false;
                
                $('.inline-group').each(function() {
                    var $container = $(this);
                    var correctCount = $container.find('input[id$="_correct"]:checked').length;
                    var choiceCount = 0;
                    
                    for (var i = 1; i <= 6; i++) {
                        var text = $container.find('input[id$="choice' + i + '_text"]').val();
                        if (text && text.trim()) {
                            choiceCount++;
                        }
                    }
                    
                    if (choiceCount >= 2 && (correctCount === 0 || correctCount > 1)) {
                        hasErrors = true;
                    }
                });
                
                if (hasErrors) {
                    alert('エラー: 各質問に対して正解を1つだけ選択し、最低2つの選択肢を入力してください。');
                    e.preventDefault();
                    return false;
                }
            });
        }
        
        // 質問削除時の確認
        function setupDeleteConfirmation() {
            $(document).on('click', '.delete-row', function(e) {
                if (!confirm('この質問とその選択肢を削除しますか？')) {
                    e.preventDefault();
                    return false;
                }
            });
        }
        
        // 初期化関数
        function initializeInlines() {
            $('.inline-group').each(function() {
                var $container = $(this);
                updateChoiceNumbering($container);
                updateCorrectChoiceHighlight($container);
                validateQuestion($container);
            });
        }
        
        // すべての機能を初期化
        setupCorrectAnswerExclusive();
        setupTextFieldValidation();
        setupCollapsible();
        setupFormValidation();
        setupDeleteConfirmation();
        initializeInlines();
        
        // 動的に追加された要素を監視
        if (window.MutationObserver) {
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length > 0) {
                        setTimeout(function() {
                            initializeInlines();
                        }, 100);
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
        
        // ショートカットキー
        $(document).on('keydown', function(e) {
            // Ctrl+S で保存
            if (e.ctrlKey && e.which === 83) {
                e.preventDefault();
                $('input[name="_save"]').click();
            }
        });
        
        // 定期的なバリデーション更新
        setInterval(function() {
            $('.inline-group').each(function() {
                validateQuestion($(this));
            });
        }, 3000);
    });
    
})(django.jQuery);