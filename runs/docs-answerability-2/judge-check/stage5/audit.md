# Tool-use audit

Batch decision: valid; expected offered tools 0; expected model claude-sonnet-5-5; expected base-dir line 137.

| run | eval id | agent | model | offered | tool_use | line | payload16 | reply16 | result | peak | in-equiv |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r001 | a03 | ad8f7b563835ab3c1 | claude-sonnet-5-5 | 0 | 0 | 137 | c05dc67dd148a782 | 2f55e3c27a085c16 | ANSWERABLE | 7709 | 9,624 |
| r002 | a05 | ae119a5a264da430c | claude-sonnet-5-5 | 0 | 0 | 137 | 23ba3d34e99d5645 | 4dfcaf407130b238 | ANSWERABLE | 7968 | 9,247 |
| r003 | a07 | a964bbf3b7124d8f5 | claude-sonnet-5-5 | 0 | 0 | 137 | 51baed3414ff5102 | 3a870edd94f3667d | NOT_ANSWERABLE | 6845 | 7,845 |
| r004 | a09 | a73e1323eed9869bb | claude-sonnet-5-5 | 0 | 0 | 137 | 3ec3796066c4fae2 | 3b3bc5f6e3c2e566 | ANSWERABLE | 8081 | 9,385 |
| r005 | a13 | a6be0588493ec0b75 | claude-sonnet-5-5 | 0 | 0 | 137 | 3e72d3f7f9ef60ae | ec0fbb2852555c8a | ANSWERABLE | 7615 | 8,805 |
| r006 | a15 | a60283b5bb10e9b71 | claude-sonnet-5-5 | 0 | 0 | 137 | 60eb5b0489aebc0a | 72306f9bfbe3e8b4 | NOT_ANSWERABLE | 10034 | 11,829 |
| r007 | a18 | ad303c36ad30900fd | claude-sonnet-5-5 | 0 | 0 | 137 | c7b11bde049d3ea2 | abfb18994000ec3c | ANSWERABLE | 6724 | 7,692 |
| r008 | a20 | a4fee349e21557db9 | claude-sonnet-5-5 | 0 | 0 | 137 | 0d0bec940553edb5 | edcc52bc32162363 | NOT_ANSWERABLE | 11146 | 13,128 |
| r009 | a22 | a8c875db91eb74e7e | claude-sonnet-5-5 | 0 | 0 | 137 | 5e7dbda4d0ba3879 | 812f49d013a00532 | ANSWERABLE | 7170 | 8,216 |
| r010 | a24 | a4c63c7b77972b9b0 | claude-sonnet-5-5 | 0 | 0 | 137 | 22a60d9094390216 | 357c6e1670f673a2 | ANSWERABLE | 9242 | 10,836 |
| r011 | u01 | a2191964e442d6adf | claude-sonnet-5-5 | 0 | 0 | 137 | 79a8ac7ed936b706 | ed495e1151b9c722 | NOT_ANSWERABLE | 8103 | 9,416 |
| r012 | u02 | ae4b0d8561ea34d6d | claude-sonnet-5-5 | 0 | 0 | 137 | fc211a043cedee49 | b95e72ec10bf024d | NOT_ANSWERABLE | 7369 | 8,498 |
| r013 | u03 | a0f48fab7fc4dc092 | claude-sonnet-5-5 | 0 | 0 | 137 | 7fb1addc0ed2a750 | 0ba6a1d948297ca8 | NOT_ANSWERABLE | 7282 | 8,388 |
| r014 | u04 | a8ede70206bb605b8 | claude-sonnet-5-5 | 0 | 0 | 137 | 118c747e4b12f007 | 91ee354943afee2d | NOT_ANSWERABLE | 8668 | 10,121 |
| r015 | u05 | aa7b0b6ba4289caba | claude-sonnet-5-5 | 0 | 0 | 137 | b1c9b7edfa5e31dd | e0159be1a599d2c4 | NOT_ANSWERABLE | 8609 | 10,047 |
| r016 | u06 | a5717b9316b720eb8 | claude-sonnet-5-5 | 0 | 0 | 137 | 9f9d2ebbdd0c917e | c1bbdbd1bd9fd0ce | NOT_ANSWERABLE | 8136 | 9,455 |
| r017 | h03 | ae1fdcf0758bdbf79 | claude-sonnet-5-5 | 0 | 0 | 137 | 028982a3ec580833 | a6270b9871058239 | ANSWERABLE | 8450 | 9,847 |
| r018 | h06 | a114e771cf4cb1e2b | claude-sonnet-5-5 | 0 | 0 | 137 | 9880072d93dc89d4 | 7e544ae7d5570a1f | ANSWERABLE | 7764 | 8,992 |
| r019 | h08 | af103e6937082f385 | claude-sonnet-5-5 | 0 | 0 | 137 | facf1e192e06b656 | e0fa1612de91f4b7 | ANSWERABLE | 6872 | 7,878 |
| r020 | h10 | aa8ff0cfe96ecbc7c | claude-sonnet-5-5 | 0 | 0 | 137 | c017e30b7351a26c | 4f749d4951c9f08a | ANSWERABLE | 7142 | 8,214 |
| r021 | h12 | a8bb470f188fa08a9 | claude-sonnet-5-5 | 0 | 0 | 137 | 631eab361bc2e663 | 6dad773533db875b | NOT_ANSWERABLE | 7082 | 8,139 |
| r022 | h16 | aa93b58b7f6b00904 | claude-sonnet-5-5 | 0 | 0 | 137 | 3d12dcb21522daf0 | 510408fa4f499d03 | ANSWERABLE | 7466 | 8,618 |
| r023 | hu01 | a25d909b4cfd394cb | claude-sonnet-5-5 | 0 | 0 | 137 | 760c2f8005517ee7 | 473a96c9d62606e4 | NOT_ANSWERABLE | 7808 | 9,046 |
| r024 | hu02 | a123e9600ab19e67d | claude-sonnet-5-5 | 0 | 0 | 137 | bd7d9d5b43fe2b2e | 35fbef8cd6c5a828 | NOT_ANSWERABLE | 8925 | 10,443 |
| r025 | hu03 | a2a2c53e312dde6ae | claude-sonnet-5-5 | 0 | 0 | 137 | c8e379dfd775b73c | 656472bebdf7a1af | NOT_ANSWERABLE | 6737 | 7,708 |
| r026 | hu04 | a22c3b2be0ff358dd | claude-sonnet-5-5 | 0 | 0 | 137 | bea3373916da9e59 | b29754c240190698 | NOT_ANSWERABLE | 7639 | 8,835 |
| r027 | hu05 | a899a848f759004ca | claude-sonnet-5-5 | 0 | 0 | 137 | aab6b5199dfd4657 | 9b873c208e41a9c3 | NOT_ANSWERABLE | 7047 | 8,096 |
| r028 | hu06 | a33f4a687ad011a83 | claude-sonnet-5-5 | 0 | 0 | 137 | 39abcfe576f81362 | 24e4df33a0bc7a51 | NOT_ANSWERABLE | 7784 | 9,018 |
| r029 | t02 | a2f453f6ec451baf5 | claude-sonnet-5-5 | 0 | 0 | 137 | ef5422e36bb9245a | bcd2be70f412110f | ANSWERABLE | 6646 | 7,592 |
| r030 | t05 | a608444913400dcba | claude-sonnet-5-5 | 0 | 0 | 137 | c6db54bc514a1ce6 | 268859e732879a49 | ANSWERABLE | 6942 | 7,964 |
| r031 | t08 | a1a001ec92385cb2f | claude-sonnet-5-5 | 0 | 0 | 137 | a3abaf134abfc08b | ed84c6d940222fe3 | ANSWERABLE | 12337 | 14,706 |
| r032 | t10 | a7a6b6bf27be467f6 | claude-sonnet-5-5 | 0 | 0 | 137 | a612133a7ea70206 | 1063c8bbdb0d4916 | ANSWERABLE | 7875 | 9,128 |
| r033 | t14 | a20641985d5e37716 | claude-sonnet-5-5 | 0 | 0 | 137 | 2125071d3eeb2f12 | a78f6339c28d43db | ANSWERABLE | 7345 | 8,465 |
| r034 | tu01 | af070fe95d546ff84 | claude-sonnet-5-5 | 0 | 0 | 137 | 6ed92cda33adb765 | d030607327786dd1 | NOT_ANSWERABLE | 7420 | 8,560 |
| r035 | tu02 | ab4a9be4532852f64 | claude-sonnet-5-5 | 0 | 0 | 137 | ba6e51571b490bf8 | 5c24f4e166e73dfe | NOT_ANSWERABLE | 9273 | 10,878 |
| r036 | tu03 | abf42049cc58d0aab | claude-sonnet-5-5 | 0 | 0 | 137 | b22c9ff68ec6cf8e | 635039e007822006 | NOT_ANSWERABLE | 8169 | 9,495 |
| r037 | tu04 | aa4be4901cc0cbb51 | claude-sonnet-5-5 | 0 | 0 | 137 | 507793ffb9ec9ae6 | e02264a301e100fd | NOT_ANSWERABLE | 7860 | 9,114 |
| r038 | f01 | a811d639ddc53a040 | claude-sonnet-5-5 | 0 | 0 | 137 | 12888aa728dca65f | 61b6af5e9e95ee7c | ANSWERABLE | 6762 | 7,712 |
| r039 | f03 | ad5d3dc977d7c2325 | claude-sonnet-5-5 | 0 | 0 | 137 | b0206f92c6d51a41 | 0b7a7cac3061c8d9 | ANSWERABLE | 8070 | 9,340 |
| r040 | f06 | a91d1bd09a824bc9b | claude-sonnet-5-5 | 0 | 0 | 137 | 9cba4a3f7850c95c | fdb5cb59df1b9561 | ANSWERABLE | 6256 | 7,106 |
| r041 | f08 | aef2bfcaab2838462 | claude-sonnet-5-5 | 0 | 0 | 137 | 76c4123109d6c99d | c71ae918d10a9f29 | ANSWERABLE | 6933 | 7,953 |
| r042 | f10 | a99399b61edc87940 | claude-sonnet-5-5 | 0 | 0 | 137 | ddce5848f3ef14a9 | ab6d75879f1bb8a8 | ANSWERABLE | 6971 | 7,998 |
| r043 | f13 | a71205b6806cfaaff | claude-sonnet-5-5 | 0 | 0 | 137 | f86287b3caedf04d | b5f526c7ae687558 | ANSWERABLE | 7435 | 8,530 |
| r044 | f15 | a48ec75f151b82197 | claude-sonnet-5-5 | 0 | 0 | 137 | 0c676e1cd7b85e10 | e2c575106cff7cc9 | ANSWERABLE | 7290 | 8,395 |
| r045 | fu01 | a0c67d0cceffd84fb | claude-sonnet-5-5 | 0 | 0 | 137 | 781b552398a3d635 | ae0e6d33704ff560 | NOT_ANSWERABLE | 9916 | 11,683 |
| r046 | fu02 | a61df281630e7165e | claude-sonnet-5-5 | 0 | 0 | 137 | 2c9c5ad6aeda0bf3 | 04bb1e765d2c25ba | NOT_ANSWERABLE | 8374 | 9,752 |
| r047 | fu03 | a00e9bb80fa554883 | claude-sonnet-5-5 | 0 | 0 | 137 | 3b608a0242a6791e | 62510093bfe79b78 | NOT_ANSWERABLE | 8239 | 9,583 |
| r048 | fu04 | ad47aca8cd7e686e0 | claude-sonnet-5-5 | 0 | 0 | 137 | 9044ae729fe9f4ce | 65a6b63c0194b129 | NOT_ANSWERABLE | 7166 | 8,245 |
| r049 (not in batch) | a04 | a05754993e5f8dd16 | claude-sonnet-5-5 | 0 | 0 | 137 | 01e660d80cf84cf4 | b264f673a619ceb9 | ANSWERABLE | 7784 | 9,716 |

Batch spawns: 48; peak sum 378,696; in-equivalent sum 439,564.
Other agents (not judge spawns, not counted): none.
