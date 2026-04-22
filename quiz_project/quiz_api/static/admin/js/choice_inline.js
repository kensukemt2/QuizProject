// 選択肢インライン管理のJavaScript
(function($) {
    'use strict';
    
    $(document).ready(function() {
        // 正解チェックボックスの排他制御
        function setupCorrectAnswerExclusive() {
            $('.field-is_correct input[type="checkbox"]').on('change', function() {
                if (this.checked) {
                    // 同じ質問内の他の正解チェックボックスを無効化
                    var $parent = $(this).closest('.inline-group, .tabular');
                    $parent.find('.field-is_correct input[type="checkbox"]').not(this).prop('checked', false);
                    
                    // 正解選択肢をハイライト
                    updateCorrectChoiceHighlight($parent);
                }
            });
        }
        
        // 正解選択肢のハイライト更新
        function updateCorrectChoiceHighlight($container) {
            $container.find('.form-row').removeClass('correct-choice');
            $container.find('.field-is_correct input[type="checkbox"]:checked').closest('.form-row').addClass('correct-choice');
        }
        
        // バリデーション
        function validateChoices() {
            $('.inline-group').each(function() {
                var $group = $(this);
                var correctCount = $group.find('.field-is_correct input[type="checkbox"]:checked').length;
                var choiceCount = $group.find('.form-row.has_original').length;
                
                // 警告クラスをリセット
                $group.removeClass('no-correct-answer multiple-correct-answers');
                
                if (choiceCount > 0) {
                    if (correctCount === 0) {
                        $group.addClass('no-correct-answer');
                        addValidationMessage($group, '警告: 正解が選択されていません');
                    } else if (correctCount > 1) {
                        $group.addClass('multiple-correct-answers');
                        addValidationMessage($group, 'エラー: 複数の正解が選択されています');
                    }
                }
            });
        }
        
        // バリデーションメッセージを追加
        function addValidationMessage($group, message) {
            $group.find('.validation-message').remove();
            $group.prepend('<div class="validation-message" style="color: #721c24; background-color: #f8d7da; padding: 8px; margin-bottom: 10px; border-radius: 4px;">' + message + '</div>');
        }
        
        // 動的に追加された要素にもイベントを適用
        function setupDynamicEvents() {
            $(document).on('change', '.field-is_correct input[type="checkbox"]', function() {
                if (this.checked) {
                    var $parent = $(this).closest('.inline-group, .tabular');
                    $parent.find('.field-is_correct input[type="checkbox"]').not(this).prop('checked', false);
                    updateCorrectChoiceHighlight($parent);
                }
                validateChoices();
            });
            
            // フォーム送信前のバリデーション
            $('form').on('submit', function(e) {
                var hasErrors = $('.multiple-correct-answers').length > 0;
                if (hasErrors) {
                    alert('エラー: 複数の正解が選択されている質問があります。修正してから送信してください。');
                    e.preventDefault();
                    return false;
                }
            });
        }
        
        // 選択肢の自動番号付け
        function updateChoiceNumbers() {
            $('.tabular').each(function() {
                var $table = $(this);
                var counter = 1;
                $table.find('.form-row.has_original').each(function() {
                    var $row = $(this);
                    var $textField = $row.find('.field-text input');
                    if ($textField.length && !$textField.val().match(/^\d+\./)) {
                        // 既に番号が付いていない場合のみ番号を追加
                        $textField.attr('placeholder', counter + '. 選択肢を入力...');
                    }
                    counter++;
                });
            });
        }
        
        // 初期化
        setupCorrectAnswerExclusive();
        setupDynamicEvents();
        updateCorrectChoiceHighlight($('.inline-group, .tabular'));
        validateChoices();
        updateChoiceNumbers();
        
        // MutationObserverで動的要素を監視
        if (window.MutationObserver) {
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length > 0) {
                        updateCorrectChoiceHighlight($('.inline-group, .tabular'));
                        validateChoices();
                        updateChoiceNumbers();
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
        
        // 定期的なチェック（フォールバック）
        setInterval(function() {
            validateChoices();
            updateChoiceNumbers();
        }, 2000);
    });
    
})(django.jQuery);